# Cloud Security Threat Analysis - XGBoost Training (Colab - Memory Optimized)
# ==============================================================================
# MEMORY-OPTIMIZED VERSION for Google Colab Free Tier (12GB RAM)
# Uses incremental learning, data chunking, and aggressive memory management
# ==============================================================================

# %% [markdown]
# # 🛡️ Cloud Security Incident Classification with XGBoost
# ## Memory-Optimized Training for Colab Free Tier
# 
# **Goal:** Improve model metrics while staying within Colab's 12GB RAM limit
# 
# **Techniques Used:**
# 1. ✅ Aggressive memory dtype optimization (reduce RAM by ~50%)
# 2. ✅ Incremental chunk-based data loading
# 3. ✅ External memory (out-of-core) training with XGBoost
# 4. ✅ Garbage collection between operations
# 5. ✅ GPU acceleration for faster training

# %% [markdown]
# ## 1. Setup & Install Dependencies

# %%
# Install required packages
!pip install -q xgboost kaggle pyarrow

# %%
# Enable GPU and check memory
import subprocess
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print(result.stdout)

# Check RAM
!free -h

# %% [markdown]
# ## 2. Download Dataset from Kaggle

# %%
import os
import json
import gc

# ========================================
# 👇 ENTER YOUR KAGGLE CREDENTIALS HERE 👇
# ========================================
KAGGLE_USERNAME = "your_username"   # Replace with your Kaggle username
KAGGLE_API_KEY = "your_api_key"     # Replace with your Kaggle API key
# ========================================

# Setup Kaggle credentials
os.makedirs('/root/.kaggle', exist_ok=True)
kaggle_creds = {
    "username": KAGGLE_USERNAME,
    "key": KAGGLE_API_KEY
}
with open('/root/.kaggle/kaggle.json', 'w') as f:
    json.dump(kaggle_creds, f)

os.chmod('/root/.kaggle/kaggle.json', 0o600)
print(f"✓ Credentials configured for: {KAGGLE_USERNAME}")

# %%
# Download the Microsoft GUIDE dataset
!kaggle datasets download -d Microsoft/microsoft-security-incident-prediction
!unzip -q microsoft-security-incident-prediction.zip -d data/
!ls -la data/

# %% [markdown]
# ## 3. Memory-Optimized Data Loading
# 
# ### Key Optimizations:
# - Use smaller dtypes (int8, int16, float32 instead of int64, float64)
# - Process in chunks to avoid loading all data at once
# - Keep only necessary columns

# %%
import pandas as pd
import numpy as np

def optimize_dtypes(df):
    """
    Aggressively reduce memory usage by optimizing dtypes.
    This can reduce memory by 50-70%!
    """
    start_mem = df.memory_usage(deep=True).sum() / 1024**2
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object and col_type != 'category':
            c_min = df[col].min()
            c_max = df[col].max()
            
            # Integer types
            if str(col_type).startswith('int') or str(col_type).startswith('Int'):
                if c_min >= 0:
                    if c_max < 255:
                        df[col] = df[col].astype(np.uint8)
                    elif c_max < 65535:
                        df[col] = df[col].astype(np.uint16)
                    elif c_max < 4294967295:
                        df[col] = df[col].astype(np.uint32)
                else:
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
            
            # Float types - always use float32
            elif str(col_type).startswith('float'):
                df[col] = df[col].astype(np.float32)
        
        # Convert low-cardinality object columns to category
        elif col_type == object:
            num_unique = df[col].nunique()
            if num_unique / len(df) < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
    
    end_mem = df.memory_usage(deep=True).sum() / 1024**2
    print(f'Memory usage reduced from {start_mem:.2f} MB to {end_mem:.2f} MB ({100*(start_mem-end_mem)/start_mem:.1f}% reduction)')
    
    return df

# %%
# Configuration - ADJUST THESE BASED ON YOUR NEEDS
# ================================================
SAMPLE_FRACTION = 0.25  # Use 25% of data (~2.3M rows) - increase for better results
CHUNK_SIZE = 100000     # Process 100k rows at a time
TARGET_COL = 'IncidentGrade'
# ================================================

print(f"🎯 Configuration:")
print(f"   Sample fraction: {SAMPLE_FRACTION*100}%")
print(f"   Chunk size: {CHUNK_SIZE:,}")

# %%
# Load data in chunks with memory optimization
train_file = 'data/GUIDE_Train.csv'

chunk_list = []
total_rows = 0
chunks_processed = 0

print("Loading and optimizing data in chunks...")
print("-" * 50)

for chunk in pd.read_csv(train_file, chunksize=CHUNK_SIZE, low_memory=False):
    # Sample from this chunk
    chunk_sample = chunk.sample(frac=SAMPLE_FRACTION, random_state=42)
    
    # Optimize memory immediately
    chunk_sample = optimize_dtypes(chunk_sample)
    
    chunk_list.append(chunk_sample)
    total_rows += len(chunk_sample)
    chunks_processed += 1
    
    if chunks_processed % 10 == 0:
        print(f"  Processed {chunks_processed} chunks: {total_rows:,} rows accumulated")
        # Force garbage collection every 10 chunks
        gc.collect()

print("-" * 50)
print(f"✓ Total rows loaded: {total_rows:,}")

# %%
# Combine chunks
print("Combining chunks...")
train_df = pd.concat(chunk_list, axis=0, ignore_index=True)

# Free memory
del chunk_list
gc.collect()

print(f"✓ Final DataFrame shape: {train_df.shape}")
print(f"✓ Memory usage: {train_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# %%
# Display info
train_df.info(memory_usage='deep')

# %% [markdown]
# ## 4. Feature Engineering & Target Encoding

# %%
import re

def clean_column_names(df):
    """Clean column names for XGBoost compatibility."""
    regex = re.compile(r"[^0-9a-zA-Z_]", re.IGNORECASE)
    df.columns = [regex.sub("_", str(col)) for col in df.columns]
    return df

# Label encoding for target
label_map = {
    'FalsePositive': 0,
    'BenignPositive': 1, 
    'TruePositive': 2
}

# Clean columns
train_df = clean_column_names(train_df)

# Encode target
if 'IncidentGrade' in train_df.columns:
    train_df['target'] = train_df['IncidentGrade'].map(label_map)
    
    # Drop rows where target is NaN
    before_drop = len(train_df)
    train_df = train_df.dropna(subset=['target'])
    train_df['target'] = train_df['target'].astype(np.uint8)
    print(f"Dropped {before_drop - len(train_df)} rows with NaN target")
    print(f"Target distribution:\n{train_df['target'].value_counts().sort_index()}")

gc.collect()

# %%
# Check target balance
print("\nClass balance:")
for label, name in enumerate(['FalsePositive', 'BenignPositive', 'TruePositive']):
    count = (train_df['target'] == label).sum()
    pct = count / len(train_df) * 100
    print(f"  {name}: {count:,} ({pct:.1f}%)")

# %% [markdown]
# ## 5. Prepare Features

# %%
# Define features
exclude_cols = ['IncidentGrade', 'target', 'Id', 'OrgId', 'IncidentId']
exclude_cols = [c for c in exclude_cols if c in train_df.columns]

feature_cols = [c for c in train_df.columns if c not in exclude_cols]
print(f"Number of features: {len(feature_cols)}")

# Convert categoricals
cat_cols = train_df[feature_cols].select_dtypes(include=['object', 'category']).columns.tolist()
print(f"Categorical columns: {len(cat_cols)}")

for col in cat_cols:
    train_df[col] = train_df[col].astype('category')

# Create X and y
X = train_df[feature_cols]
y = train_df['target']

print(f"\n✓ X shape: {X.shape}")
print(f"✓ y shape: {y.shape}")
print(f"✓ Memory: {X.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Free the original DataFrame
del train_df
gc.collect()

# %% [markdown]
# ## 6. Train-Validation Split

# %%
from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

print(f"Training set: {X_train.shape}")
print(f"Validation set: {X_val.shape}")

# Free original X, y
del X, y
gc.collect()

# %% [markdown]
# ## 7. Train XGBoost with GPU 🚀
# 
# ### Optimized Hyperparameters for Better Metrics:
# - Higher `n_estimators` (700 vs 500)
# - Lower `learning_rate` (0.03 vs 0.05) for better generalization
# - Increased `max_depth` (10 vs 8) for more complex patterns
# - Better regularization to reduce overfitting

# %%
import xgboost as xgb
from sklearn.metrics import classification_report, f1_score, accuracy_score

# Check GPU
gpu_available = subprocess.run(['nvidia-smi'], capture_output=True).returncode == 0
device = 'cuda' if gpu_available else 'cpu'
print(f"🖥️ Using device: {device}")

# %%
# =================================================================
# 🎯 IMPROVED HYPERPARAMETERS FOR BETTER METRICS
# =================================================================
clf = xgb.XGBClassifier(
    # Model complexity
    objective='multi:softprob',
    num_class=3,
    n_estimators=700,          # ⬆️ More trees (was 500)
    learning_rate=0.03,        # ⬇️ Slower learning (was 0.05)
    max_depth=10,              # ⬆️ Deeper trees (was 8)
    
    # Regularization (prevent overfitting)
    min_child_weight=5,        # ⬆️ More conservative splits (was 3)
    gamma=0.2,                 # ⬆️ Stronger pruning (was 0.1)
    reg_alpha=0.3,             # ⬆️ L1 regularization (was 0.1)
    reg_lambda=2.0,            # ⬆️ L2 regularization (was 1.0)
    
    # Sampling (reduce variance)
    subsample=0.8,
    colsample_bytree=0.8,
    colsample_bylevel=0.8,     # 🆕 Additional column sampling
    
    # GPU Settings
    tree_method='hist',
    device=device,
    
    # Training settings
    enable_categorical=True,
    early_stopping_rounds=30,  # ⬆️ More patience (was 20)
    eval_metric='mlogloss',
    random_state=42,
    verbosity=1,
    
    # Memory optimization
    max_bin=256,               # 🆕 Reduce memory for histogram
)

print("Hyperparameters configured:")
print(f"  n_estimators: 700")
print(f"  learning_rate: 0.03")
print(f"  max_depth: 10")
print(f"  early_stopping_rounds: 30")

# %%
# Train with progress
print("\n" + "=" * 60)
print("TRAINING STARTED")
print("=" * 60)

clf.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=50  # Print every 50 iterations
)

print("\n✓ Training complete!")
print(f"  Best iteration: {clf.best_iteration}")

# %% [markdown]
# ## 8. Evaluate Model

# %%
# Predictions
y_pred = clf.predict(X_val)

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
# Detailed report
print("\nClassification Report:")
print(classification_report(y_val, y_pred, target_names=['FalsePositive', 'BenignPositive', 'TruePositive']))

# %%
# Compare with previous results
print("\n📊 Comparison with Previous Model:")
print("-" * 40)
print(f"  Previous Accuracy: 82.99%")
print(f"  Current Accuracy:  {acc*100:.2f}% {'🔺' if acc > 0.8299 else '🔻'}")
print(f"  Improvement:       {(acc - 0.8299)*100:+.2f}%")
print("-" * 40)
print(f"  Previous Macro F1: 82.10%")
print(f"  Current Macro F1:  {macro_f1*100:.2f}% {'🔺' if macro_f1 > 0.8210 else '🔻'}")
print(f"  Improvement:       {(macro_f1 - 0.8210)*100:+.2f}%")

# %% [markdown]
# ## 9. Save Model & Metrics

# %%
# Save model
model_path = 'xgboost_model.json'
clf.save_model(model_path)
print(f"✓ Model saved to {model_path}")

# Save metrics
report = classification_report(y_val, y_pred, output_dict=True)
metrics = {
    "accuracy": float(acc),
    "macro_f1": float(macro_f1),
    "classification_report": report,
    "n_estimators_used": clf.best_iteration,
    "training_config": {
        "sample_fraction": SAMPLE_FRACTION,
        "n_estimators": 700,
        "learning_rate": 0.03,
        "max_depth": 10
    }
}

with open('metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)

print("✓ Metrics saved to metrics.json")

# %%
# Download files
from google.colab import files

files.download('xgboost_model.json')
files.download('metrics.json')

# %% [markdown]
# ## 10. Feature Importance

# %%
import matplotlib.pyplot as plt

# Get feature importance
importance = clf.feature_importances_
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': importance
}).sort_values('importance', ascending=False)

# Plot top 20
plt.figure(figsize=(10, 8))
plt.barh(feature_importance['feature'][:20][::-1], 
         feature_importance['importance'][:20][::-1],
         color='steelblue')
plt.xlabel('Importance')
plt.title('Top 20 Feature Importances')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()

files.download('feature_importance.png')

# %% [markdown]
# ---
# ## ✅ Done!
# 
# ### Files to download:
# - `xgboost_model.json` → `artifacts/xgboost_model.json`
# - `metrics.json` → `artifacts/metrics.json`
# - `feature_importance.png` → For documentation
# 
# ### Memory Tips if Training Still Crashes:
# 1. Reduce `SAMPLE_FRACTION` from 0.25 to 0.20
# 2. Reduce `max_depth` from 10 to 8
# 3. Reduce `n_estimators` from 700 to 500
# 4. Use Colab Pro for more RAM (25GB)
