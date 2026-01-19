# Cloud Security Threat Analysis - XGBoost Training (BULLETPROOF VERSION)
# ==========================================================================
# CPU-BASED TRAINING - Slower but STABLE, won't crash
# Estimated time: ~20-25 minutes
# ==========================================================================

# %% [markdown]
# # 🛡️ Cloud Security Incident Classification
# ## Bulletproof CPU Training (No GPU Memory Issues)

# %%
!pip install -q xgboost kaggle

# %%
import subprocess
print("GPU Info:")
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print(result.stdout if result.returncode == 0 else "No GPU")
print("\nRAM Info:")
!free -h

# %%
import os
import json
import gc
import time
import warnings
warnings.filterwarnings('ignore')

# ========================================
# 👇 ENTER YOUR KAGGLE CREDENTIALS HERE 👇
# ========================================
KAGGLE_USERNAME = "your_username"
KAGGLE_API_KEY = "your_api_key"
# ========================================

os.makedirs('/root/.kaggle', exist_ok=True)
with open('/root/.kaggle/kaggle.json', 'w') as f:
    json.dump({"username": KAGGLE_USERNAME, "key": KAGGLE_API_KEY}, f)
os.chmod('/root/.kaggle/kaggle.json', 0o600)
print(f"✓ Kaggle configured")

# %%
# Download dataset (skip if already downloaded)
import os
if not os.path.exists('data/GUIDE_Train.csv'):
    !kaggle datasets download -d Microsoft/microsoft-security-incident-prediction
    !unzip -q -o microsoft-security-incident-prediction.zip -d data/
else:
    print("✓ Data already downloaded")
!ls -la data/

# %% [markdown]
# ## Load Data - Conservative Memory Settings

# %%
import pandas as pd
import numpy as np
import re

# ============================================
# 🎯 CONSERVATIVE SETTINGS - WILL NOT CRASH
# ============================================
SAMPLE_ROWS = 800_000  # ~800K rows (safe for 12GB RAM)
# ============================================

TRAIN_FILE = 'data/GUIDE_Train.csv'

# Count rows efficiently
print("Counting rows...")
with open(TRAIN_FILE, 'r') as f:
    total_rows = sum(1 for _ in f) - 1
print(f"Total: {total_rows:,}")
print(f"Using: {SAMPLE_ROWS:,} ({SAMPLE_ROWS/total_rows*100:.1f}%)")

# %%
# Load with sampling
print("\nLoading data...")
start = time.time()

np.random.seed(42)
sample_rate = SAMPLE_ROWS / total_rows
skiprows = lambda x: x > 0 and np.random.random() > sample_rate

train_df = pd.read_csv(TRAIN_FILE, skiprows=skiprows, low_memory=False)

print(f"✓ Loaded {len(train_df):,} rows in {time.time()-start:.0f}s")

# %%
# Memory optimization
def optimize_mem(df):
    for col in df.columns:
        dtype = df[col].dtype
        if dtype == 'object':
            if df[col].nunique() < 500:
                df[col] = df[col].astype('category')
        elif 'int' in str(dtype):
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif 'float' in str(dtype):
            df[col] = pd.to_numeric(df[col], downcast='float')
    return df

train_df = optimize_mem(train_df)
gc.collect()

mem_mb = train_df.memory_usage(deep=True).sum() / 1024**2
print(f"Memory: {mem_mb:.0f} MB")

# %%
# Clean & encode
regex = re.compile(r"[^0-9a-zA-Z_]")
train_df.columns = [regex.sub("_", str(c)) for c in train_df.columns]

label_map = {'FalsePositive': 0, 'BenignPositive': 1, 'TruePositive': 2}
train_df['target'] = train_df['IncidentGrade'].map(label_map)
train_df = train_df.dropna(subset=['target'])
train_df['target'] = train_df['target'].astype('int8')

print(f"Shape: {train_df.shape}")
print(train_df['target'].value_counts().sort_index())

# %%
# Prepare features
exclude = ['IncidentGrade', 'target', 'Id', 'OrgId', 'IncidentId']
exclude = [c for c in exclude if c in train_df.columns]
features = [c for c in train_df.columns if c not in exclude]

for col in train_df[features].select_dtypes(include=['object', 'category']).columns:
    train_df[col] = train_df[col].astype('category')

X = train_df[features].copy()
y = train_df['target'].copy()

del train_df
gc.collect()

print(f"Features: {len(features)}")

# %%
# Split
from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

del X, y
gc.collect()

print(f"Train: {len(X_train):,}, Val: {len(X_val):,}")

# %%
# Check memory before training
!free -h

# %% [markdown]
# ## Train XGBoost - CPU ONLY (Stable)

# %%
import xgboost as xgb
from sklearn.metrics import classification_report, f1_score, accuracy_score

# ============================================
# 🎯 CPU TRAINING - STABLE, NO GPU CRASHES
# ============================================
clf = xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=3,
    
    # Conservative settings
    n_estimators=400,
    max_depth=6,
    learning_rate=0.08,
    
    min_child_weight=5,
    gamma=0.2,
    reg_alpha=0.3,
    reg_lambda=2.0,
    
    subsample=0.8,
    colsample_bytree=0.8,
    
    # ⚠️ CPU ONLY - NO GPU
    tree_method='hist',
    device='cpu',           # <-- FORCE CPU
    n_jobs=-1,              # Use all CPU cores
    
    enable_categorical=True,
    early_stopping_rounds=20,
    eval_metric='mlogloss',
    random_state=42,
    verbosity=1,
)

print("📊 Training Configuration:")
print("  Device: CPU (stable)")
print("  n_estimators: 400")
print("  max_depth: 6")
print(f"  Training samples: {len(X_train):,}")

# %%
print("\n" + "=" * 60)
print("🚀 TRAINING STARTED (CPU MODE)")
print("⏱️ Expected time: ~15-20 minutes")
print("=" * 60)

start = time.time()

clf.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=20  # Print every 20 iterations
)

elapsed = time.time() - start
print(f"\n✓ Done in {elapsed/60:.1f} minutes")
print(f"  Best iteration: {clf.best_iteration}")

# %% [markdown]
# ## Evaluate

# %%
y_pred = clf.predict(X_val)

acc = accuracy_score(y_val, y_pred)
macro_f1 = f1_score(y_val, y_pred, average='macro')

print("\n" + "=" * 60)
print("🎯 RESULTS")
print("=" * 60)
print(f"  Accuracy:  {acc*100:.2f}%")
print(f"  Macro F1:  {macro_f1*100:.2f}%")
print("=" * 60)

print("\nDetailed Report:")
print(classification_report(y_val, y_pred, 
      target_names=['FalsePositive', 'BenignPositive', 'TruePositive']))

# %%
# Compare
print("\n📊 vs Previous Model:")
print(f"  Previous: Acc 82.99%, F1 82.10%")
print(f"  Current:  Acc {acc*100:.2f}%, F1 {macro_f1*100:.2f}%")
print(f"  Change:   Acc {(acc-0.8299)*100:+.2f}%, F1 {(macro_f1-0.8210)*100:+.2f}%")

# %% [markdown]
# ## Save & Download

# %%
# Save model
clf.save_model('xgboost_model.json')

# Save metrics
metrics = {
    "accuracy": float(acc),
    "macro_f1": float(macro_f1),
    "classification_report": classification_report(y_val, y_pred, output_dict=True),
    "n_estimators_used": clf.best_iteration,
    "training_samples": len(X_train),
    "training_time_minutes": round(elapsed/60, 1),
    "device": "cpu"
}

with open('metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)

print("✓ Model and metrics saved")

# %%
from google.colab import files
files.download('xgboost_model.json')
files.download('metrics.json')

# %%
# Optional: Feature importance
import matplotlib.pyplot as plt

fi = pd.DataFrame({
    'feature': features, 
    'importance': clf.feature_importances_
}).sort_values('importance', ascending=False)

plt.figure(figsize=(10,6))
plt.barh(fi['feature'][:15][::-1], fi['importance'][:15][::-1])
plt.title('Top 15 Features')
plt.tight_layout()
plt.savefig('features.png', dpi=100)
plt.show()

files.download('features.png')

print("\n✅ ALL DONE!")
