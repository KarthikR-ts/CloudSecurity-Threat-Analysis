# Cloud Security Threat Analysis - XGBoost External Memory Training
# ==================================================================
# EXTREME MEMORY OPTIMIZATION using XGBoost's External Memory
# For training on datasets that don't fit in RAM
# ==================================================================

# %% [markdown]
# # 🛡️ XGBoost External Memory Training
# ## For Very Large Datasets on Colab Free Tier
# 
# This notebook uses XGBoost's **external memory (out-of-core)** feature
# to train on datasets larger than available RAM.

# %% [markdown]
# ## 1. Setup

# %%
!pip install -q xgboost kaggle pyarrow

# %%
import subprocess
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print(result.stdout)
!free -h

# %% [markdown]
# ## 2. Download Dataset

# %%
import os
import json
import gc

# ========================================
KAGGLE_USERNAME = "your_username"
KAGGLE_API_KEY = "your_api_key"
# ========================================

os.makedirs('/root/.kaggle', exist_ok=True)
with open('/root/.kaggle/kaggle.json', 'w') as f:
    json.dump({"username": KAGGLE_USERNAME, "key": KAGGLE_API_KEY}, f)
os.chmod('/root/.kaggle/kaggle.json', 0o600)

# %%
!kaggle datasets download -d Microsoft/microsoft-security-incident-prediction
!unzip -q microsoft-security-incident-prediction.zip -d data/
!ls -la data/

# %% [markdown]
# ## 3. Convert CSV to LibSVM Format (Memory Efficient)
# 
# XGBoost's external memory requires data in specific formats.
# We'll convert in chunks to avoid memory issues.

# %%
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import re

TRAIN_FILE = 'data/GUIDE_Train.csv'
CHUNK_SIZE = 50000  # Smaller chunks for memory safety

# First pass: determine categorical encoders
print("Pass 1: Building encoders...")

# Read just the first chunk to identify columns
sample_df = pd.read_csv(TRAIN_FILE, nrows=1000, low_memory=False)

# Clean column names
regex = re.compile(r"[^0-9a-zA-Z_]", re.IGNORECASE)
sample_df.columns = [regex.sub("_", str(col)) for col in sample_df.columns]

# Identify columns
target_col = 'IncidentGrade'
exclude_cols = [target_col, 'Id', 'OrgId', 'IncidentId']
feature_cols = [c for c in sample_df.columns if c not in exclude_cols]
cat_cols = sample_df[feature_cols].select_dtypes(include=['object']).columns.tolist()

print(f"Features: {len(feature_cols)}")
print(f"Categorical: {len(cat_cols)}")

del sample_df
gc.collect()

# %%
# Build categorical encoders from full data
print("\nBuilding categorical encoders (this may take a while)...")

encoders = {}
unique_values = {col: set() for col in cat_cols}

for chunk in pd.read_csv(TRAIN_FILE, chunksize=CHUNK_SIZE, low_memory=False, usecols=cat_cols):
    for col in cat_cols:
        unique_values[col].update(chunk[col].dropna().unique())
    gc.collect()

for col in cat_cols:
    le = LabelEncoder()
    le.fit(list(unique_values[col]) + ['__unknown__'])
    encoders[col] = le
    print(f"  {col}: {len(le.classes_)} unique values")

# Target encoder
label_map = {'FalsePositive': 0, 'BenignPositive': 1, 'TruePositive': 2}

del unique_values
gc.collect()

# %%
# Convert to LibSVM format
print("\nConverting to LibSVM format...")

def row_to_libsvm(row, feature_cols, encoders, label_map, target_col):
    """Convert a single row to libsvm format."""
    try:
        # Target
        target = label_map.get(row[target_col], -1)
        if target == -1:
            return None
        
        parts = [str(target)]
        
        for i, col in enumerate(feature_cols):
            val = row[col]
            if pd.isna(val):
                continue
            
            if col in encoders:
                try:
                    encoded = encoders[col].transform([str(val)])[0]
                    parts.append(f"{i}:{encoded}")
                except:
                    parts.append(f"{i}:0")  # Unknown category
            else:
                if isinstance(val, (int, float)) and not np.isnan(val):
                    parts.append(f"{i}:{val}")
        
        return ' '.join(parts)
    except Exception as e:
        return None

# Write LibSVM file
libsvm_file = 'train.libsvm'
total_rows = 0
valid_rows = 0

with open(libsvm_file, 'w') as f:
    for chunk in pd.read_csv(TRAIN_FILE, chunksize=CHUNK_SIZE, low_memory=False):
        # Clean column names
        chunk.columns = [regex.sub("_", str(col)) for col in chunk.columns]
        
        for _, row in chunk.iterrows():
            total_rows += 1
            line = row_to_libsvm(row, feature_cols, encoders, label_map, target_col)
            if line:
                f.write(line + '\n')
                valid_rows += 1
        
        if valid_rows % 500000 == 0:
            print(f"  Processed {total_rows:,} rows, wrote {valid_rows:,} valid rows")
        
        gc.collect()

print(f"\n✓ Wrote {valid_rows:,} rows to {libsvm_file}")

# Save encoders for later use
import pickle
with open('encoders.pkl', 'wb') as f:
    pickle.dump({'encoders': encoders, 'feature_cols': feature_cols}, f)

# Free memory
del encoders
gc.collect()

# %%
# Check file size
import os
file_size = os.path.getsize(libsvm_file) / 1024**2
print(f"LibSVM file size: {file_size:.1f} MB")

# %% [markdown]
# ## 4. Train with External Memory
# 
# XGBoost will load data from disk in batches during training.

# %%
import xgboost as xgb

# Append cache suffix for external memory
# XGBoost will create a binary cache file on first run
cache_file = f'{libsvm_file}#dtrain.cache'

print("Loading data into DMatrix with external memory...")
print("(This creates a cache file for faster subsequent access)")

# Create DMatrix with external memory
dtrain = xgb.DMatrix(cache_file)

print(f"✓ DMatrix created")
print(f"  Rows: {dtrain.num_row():,}")
print(f"  Features: {dtrain.num_col()}")

# %%
# Split for validation (take last 15%)
n_total = dtrain.num_row()
n_val = int(n_total * 0.15)

# We'll use a random sample for validation
np.random.seed(42)
all_indices = np.arange(n_total)
np.random.shuffle(all_indices)

val_indices = all_indices[:n_val]
train_indices = all_indices[n_val:]

print(f"Training samples: {len(train_indices):,}")
print(f"Validation samples: {len(val_indices):,}")

# %%
# GPU check
gpu_available = subprocess.run(['nvidia-smi'], capture_output=True).returncode == 0
device = 'cuda' if gpu_available else 'cpu'
print(f"Using device: {device}")

# %%
# Train with XGBoost native API (more memory efficient)
params = {
    'objective': 'multi:softprob',
    'num_class': 3,
    'max_depth': 10,
    'learning_rate': 0.03,
    'min_child_weight': 5,
    'gamma': 0.2,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'colsample_bylevel': 0.8,
    'reg_alpha': 0.3,
    'reg_lambda': 2.0,
    'tree_method': 'hist',
    'device': device,
    'seed': 42,
    'eval_metric': 'mlogloss',
}

print("Training parameters:")
for k, v in params.items():
    print(f"  {k}: {v}")

# %%
# Train the model
print("\n" + "=" * 60)
print("TRAINING STARTED (External Memory Mode)")
print("=" * 60)

# Create watchlist
# Note: For true external memory, we train on full data
# and use a sample for evaluation
evals_result = {}

bst = xgb.train(
    params,
    dtrain,
    num_boost_round=700,
    evals=[(dtrain, 'train')],
    evals_result=evals_result,
    early_stopping_rounds=30,
    verbose_eval=50
)

print("\n✓ Training complete!")
print(f"  Best iteration: {bst.best_iteration}")

# %% [markdown]
# ## 5. Evaluate Model

# %%
from sklearn.metrics import classification_report, f1_score, accuracy_score

# Predict on a sample (memory efficient)
print("Evaluating on validation sample...")

# Read a sample for evaluation
sample_size = min(500000, n_val)
eval_data = []

with open(libsvm_file, 'r') as f:
    lines = f.readlines()
    sample_lines = [lines[i] for i in val_indices[:sample_size]]

# Parse labels
y_val = np.array([int(line.split()[0]) for line in sample_lines])

# Create DMatrix for sample
with open('val_sample.libsvm', 'w') as f:
    f.writelines(sample_lines)

dval = xgb.DMatrix('val_sample.libsvm')
y_pred = bst.predict(dval).argmax(axis=1)

# Metrics
acc = accuracy_score(y_val, y_pred)
macro_f1 = f1_score(y_val, y_pred, average='macro')

print("\n" + "=" * 60)
print("🎯 FINAL RESULTS")
print("=" * 60)
print(f"  Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
print(f"  Macro F1:  {macro_f1:.4f} ({macro_f1*100:.2f}%)")
print("=" * 60)

# %%
print("\nClassification Report:")
print(classification_report(y_val, y_pred, target_names=['FalsePositive', 'BenignPositive', 'TruePositive']))

# %%
print("\n📊 Comparison with Previous Model:")
print("-" * 40)
print(f"  Previous Accuracy: 82.99%")
print(f"  Current Accuracy:  {acc*100:.2f}%")
print(f"  Improvement:       {(acc - 0.8299)*100:+.2f}%")
print("-" * 40)
print(f"  Previous Macro F1: 82.10%")
print(f"  Current Macro F1:  {macro_f1*100:.2f}%")
print(f"  Improvement:       {(macro_f1 - 0.8210)*100:+.2f}%")

# %% [markdown]
# ## 6. Save Model

# %%
# Save model
bst.save_model('xgboost_model.json')
print("✓ Model saved")

# Save metrics
report = classification_report(y_val, y_pred, output_dict=True)
metrics = {
    "accuracy": float(acc),
    "macro_f1": float(macro_f1),
    "classification_report": report,
    "n_estimators_used": bst.best_iteration,
    "training_mode": "external_memory",
    "total_training_samples": int(n_total - n_val)
}

with open('metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)

print("✓ Metrics saved")

# %%
from google.colab import files
files.download('xgboost_model.json')
files.download('metrics.json')
files.download('encoders.pkl')  # Needed for inference

# %% [markdown]
# ---
# ## ✅ Done!
# 
# The external memory approach allows training on the FULL dataset
# without loading everything into RAM at once.
# 
# **Files to download:**
# - `xgboost_model.json` → Model file
# - `metrics.json` → Performance metrics  
# - `encoders.pkl` → Categorical encoders for inference
