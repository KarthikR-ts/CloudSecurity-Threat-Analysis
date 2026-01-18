# Cloud Security Threat Analysis - XGBoost Training (Colab)
# ============================================================
# Run this notebook in Google Colab with GPU runtime enabled
# Dataset: Microsoft GUIDE (Security Incident Prediction)
# ============================================================

# %% [markdown]
# # 🛡️ Cloud Security Incident Classification with XGBoost
# 
# This notebook trains an XGBoost model to classify security incidents as:
# - **True Positive (TP)**: Real threats requiring action
# - **Benign Positive (BP)**: Suspicious but legitimate activity
# - **False Positive (FP)**: Non-threatening false alarms

# %% [markdown]
# ## 1. Setup & Install Dependencies

# %%
# Install required packages
!pip install -q xgboost kaggle pyarrow

# %%
# Enable GPU
import subprocess
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print(result.stdout)

# %% [markdown]
# ## 2. Download Dataset from Kaggle
# 
# Enter your Kaggle credentials below.
# Get your API key from: https://www.kaggle.com/settings → API → Create New Token

# %%
import os
import json

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

# %%
# Check what files we have
!ls -la data/

# %% [markdown]
# ## 3. Load and Prepare Data

# %%
import pandas as pd
import numpy as np

# Load the dataset (adjust filename based on what's in the zip)
# The dataset typically has train.csv and test.csv
train_file = 'data/GUIDE_Train.csv'  # Adjust if different
test_file = 'data/GUIDE_Test.csv'    # Adjust if different

# Check if files exist
import os
if os.path.exists(train_file):
    print("Reading CSV data in chunks to save memory...")
    chunk_list = []
    total_rows = 0
    
    # ⚠️ OPTIMIZATION: Read in chunks of 200k rows
    # Sample 15% of each chunk to get ~1.4M rows total (from ~9.4M)
    # This keeps memory usage low during loading
    for i, chunk in enumerate(pd.read_csv(train_file, chunksize=200000)):
        chunk_sample = chunk.sample(frac=0.15, random_state=42)
        chunk_list.append(chunk_sample)
        total_rows += len(chunk_sample)
        if i % 5 == 0:
            print(f"  Processed chunk {i+1}: accumulated {total_rows} rows")
            
    # Combine all chunks
    train_df = pd.concat(chunk_list, axis=0)
    print(f"Final Sampled Train shape: {train_df.shape}")
    
    # Clean up
    del chunk_list
    import gc
    gc.collect()

else:
    # Try to find the actual files
    !ls -la data/
    print("\n⚠️ Please update the file paths above based on the actual filenames")

# %%
# Display first rows
train_df.head()

# %%
# Check columns
print("Columns:", train_df.columns.tolist())
print("\nDtypes:")
print(train_df.dtypes)

# %%
# Check target distribution
target_col = 'IncidentGrade'  # Adjust based on actual column name
if target_col in train_df.columns:
    print(train_df[target_col].value_counts(normalize=True))

# %% [markdown]
# ## 4. Feature Engineering

# %%
import re

def clean_column_names(df):
    """Clean column names for XGBoost compatibility."""
    regex = re.compile(r"[^0-9a-zA-Z_]", re.IGNORECASE)
    df.columns = [regex.sub("_", str(col)) for col in df.columns]
    return df

def encode_target(df, target_col='IncidentGrade'):
    """Encode target variable."""
    # Mapping: FalsePositive=0, BenignPositive=1, TruePositive=2
    label_map = {
        'FalsePositive': 0,
        'BenignPositive': 1, 
        'TruePositive': 2
    }
    
    if target_col in df.columns:
        df['IncidentGrade_Encoded'] = df[target_col].map(label_map)
    
    return df

# %%
# Clean and encode
train_df = clean_column_names(train_df)
train_df = encode_target(train_df, 'IncidentGrade')

# Check encoding
print("Target distribution (before cleaning):")
print(train_df['IncidentGrade_Encoded'].value_counts(dropna=False))

# ⚠️ FIX: Drop rows where target is NaN (approx 7k rows in 1.4M)
train_df = train_df.dropna(subset=['IncidentGrade_Encoded'])
print(f"Shape after dropping NaN targets: {train_df.shape}")

print("Final Target distribution:")
print(train_df['IncidentGrade_Encoded'].value_counts())

# %%
# Identify categorical columns
cat_cols = train_df.select_dtypes(include=['object', 'category']).columns.tolist()

# Remove target from categorical
if 'IncidentGrade' in cat_cols:
    cat_cols.remove('IncidentGrade')

print(f"Categorical columns ({len(cat_cols)}): {cat_cols}")

# Convert to category type
for col in cat_cols:
    train_df[col] = train_df[col].astype('category')

# %% [markdown]
# ## 5. Prepare Features and Target

# %%
# Define target
target = 'IncidentGrade_Encoded'

# Features to exclude
exclude_cols = ['IncidentGrade', 'IncidentGrade_Encoded', 'Id', 'OrgId', 'IncidentId']
exclude_cols = [c for c in exclude_cols if c in train_df.columns]

# Create feature matrix
feature_cols = [c for c in train_df.columns if c not in exclude_cols]
print(f"Number of features: {len(feature_cols)}")

X = train_df[feature_cols]
y = train_df[target]

print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")

# %%
# Train-validation split
from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

print(f"Training set: {X_train.shape}")
print(f"Validation set: {X_val.shape}")

# %% [markdown]
# ## 6. Train XGBoost with GPU 🚀

# %%
import xgboost as xgb
from sklearn.metrics import classification_report, f1_score, accuracy_score

# Check GPU availability
gpu_available = True
try:
    import subprocess
    result = subprocess.run(['nvidia-smi'], capture_output=True)
    if result.returncode != 0:
        gpu_available = False
except:
    gpu_available = False

device = 'cuda' if gpu_available else 'cpu'
print(f"Using device: {device}")

# %%
# Initialize XGBoost with GPU
clf = xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=3,
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    min_child_weight=3,
    gamma=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    tree_method='hist',
    device=device,
    enable_categorical=True,
    early_stopping_rounds=20,
    eval_metric='mlogloss',
    verbosity=1
)

# %%
# Train the model
print("Training XGBoost...")
clf.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=True
)

# %% [markdown]
# ## 7. Evaluate Model

# %%
# Predictions
y_pred = clf.predict(X_val)

# Metrics
acc = accuracy_score(y_val, y_pred)
macro_f1 = f1_score(y_val, y_pred, average='macro')

print("\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)
print(f"Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
print(f"Macro F1:  {macro_f1:.4f} ({macro_f1*100:.2f}%)")
print("=" * 60)

# %%
# Detailed classification report
print("\nClassification Report:")
print(classification_report(y_val, y_pred, target_names=['FalsePositive', 'BenignPositive', 'TruePositive']))

# %% [markdown]
# ## 8. Save Model

# %%
# Save model
model_path = 'xgboost_model.json'
clf.save_model(model_path)
print(f"Model saved to {model_path}")

# Save metrics
import json
metrics = {
    "accuracy": float(acc),
    "macro_f1": float(macro_f1),
    "n_estimators_used": clf.best_iteration if hasattr(clf, 'best_iteration') else 500
}

with open('metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)

print("Metrics saved to metrics.json")

# %%
# Download the files
from google.colab import files

files.download('xgboost_model.json')
files.download('metrics.json')

# %% [markdown]
# ## 9. Feature Importance

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
         feature_importance['importance'][:20][::-1])
plt.xlabel('Importance')
plt.title('Top 20 Feature Importances')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=150)
plt.show()

files.download('feature_importance.png')

# %% [markdown]
# ---
# ## ✅ Done!
# 
# Download the following files and place them in your project:
# - `xgboost_model.json` → `artifacts/xgboost_model.json`
# - `metrics.json` → `artifacts/metrics.json`
# - `feature_importance.png` → For documentation
