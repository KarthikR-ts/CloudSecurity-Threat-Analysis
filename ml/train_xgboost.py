
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, f1_score, confusion_matrix, accuracy_score
import json
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
import subprocess

# =============================================================================
# SETUP
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE_TRAIN = BASE_DIR / "backend" / "data" / "train_ml_ready.parquet"
DATA_FILE_TEST = BASE_DIR / "backend" / "data" / "test_ml_ready.parquet"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = ARTIFACTS_DIR / "xgboost_model.json"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"

def check_gpu_availability():
    """Check if NVIDIA GPU with CUDA is available."""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("=" * 60)
            print("GPU DETECTED - Using CUDA acceleration")
            print("=" * 60)
            return True
    except FileNotFoundError:
        pass
    print("No GPU detected, using CPU")
    return False

def load_data():
    print("Loading data...")
    if not DATA_FILE_TRAIN.exists() or not DATA_FILE_TEST.exists():
        raise FileNotFoundError(f"Data files not found at {BASE_DIR}")
        
    train_df = pd.read_parquet(DATA_FILE_TRAIN)
    test_df = pd.read_parquet(DATA_FILE_TEST)
    
    print(f"Train shape: {train_df.shape}")
    print(f"Test shape: {test_df.shape}")
    
    return train_df, test_df


def prepare_data(train_df, test_df):
    target_col = "IncidentGrade_Encoded"
    
    # Identify categorical columns (object or category)
    cat_cols = train_df.select_dtypes(include=['object', 'category']).columns.tolist()
    # Remove target from cat_cols if present (though it shouldn't be object usually)
    if target_col in cat_cols:
        cat_cols.remove(target_col)
        
    print(f"Categorical columns found: {cat_cols}")
    
    # Convert to category type for XGBoost native support
    for col in cat_cols:
        train_df[col] = train_df[col].astype("category")
        if col in test_df.columns:
            test_df[col] = test_df[col].astype("category")
    
    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]
    
    X_test = test_df.drop(columns=[target_col])
    
    if target_col in test_df.columns:
        y_test = test_df[target_col]
    else:
        y_test = None
        print("Warning: No target column in test dataset.")

    return X_train, y_train, X_test, y_test

def train_model(X_train, y_train, X_val, y_val, use_gpu=False):
    """
    Train XGBoost model with GPU acceleration if available.
    
    Optimized hyperparameters for better Macro-F1 on imbalanced security data.
    """
    print("Training XGBoost model...")
    
    # Set tree method based on GPU availability
    if use_gpu:
        tree_method = 'hist'
        device = 'cuda'
        print(f"Using GPU acceleration: tree_method={tree_method}, device={device}")
    else:
        tree_method = 'hist'
        device = 'cpu'
        print(f"Using CPU: tree_method={tree_method}")
    
    # Initialize XGBoost Classifier with optimized hyperparameters
    clf = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,            # 0=FP, 1=BP, 2=TP
        n_estimators=500,       # More trees for better performance
        learning_rate=0.05,     # Lower LR with more estimators
        max_depth=8,            # Deeper trees for complex patterns
        min_child_weight=3,     # Regularization
        gamma=0.1,              # Minimum loss reduction for split
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,          # L1 regularization
        reg_lambda=1.0,         # L2 regularization
        n_jobs=-1,
        random_state=42,
        tree_method=tree_method,
        device=device,
        enable_categorical=True,
        early_stopping_rounds=20,  # More patience for convergence
        eval_metric='mlogloss'
    )
    
    print("\nHyperparameters:")
    print(f"  n_estimators: 500")
    print(f"  learning_rate: 0.05")
    print(f"  max_depth: 8")
    print(f"  device: {device}")
    print()
    
    clf.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=True
    )
    
    return clf


def evaluate_model(clf, X_test, y_test):
    print("Evaluating model...")
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
    print(f"Macro F1:  {macro_f1:.4f} ({macro_f1*100:.2f}%)")
    print("=" * 60)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save metrics
    metrics = {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "classification_report": report
    }
    
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
    
    print(f"\nMetrics saved to {METRICS_PATH}")
        
    return metrics

def clean_column_names(df):
    import re
    regex = re.compile(r"[^0-9a-zA-Z_]", re.IGNORECASE)
    new_cols = []
    print("DEBUG: Cleaning columns started.")
    for i, col in enumerate(df.columns):
        try:
            old_name = str(col)
            new_name = regex.sub("_", old_name)
            new_cols.append(new_name)
        except Exception as e:
            print(f"CRASH on column index {i}: {e}")
            raise e
    df.columns = new_cols
    print("DEBUG: Cleaning columns finished.")
    return df


import argparse

def main():
    parser = argparse.ArgumentParser(description="Train XGBoost Model")
    parser.add_argument("--sample", type=int, default=None, help="Number of rows to sample for training")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU even if available")
    args = parser.parse_args()

    try:
        # Check GPU availability
        use_gpu = check_gpu_availability() and not args.no_gpu
        
        train_df, test_df = load_data()
        
        # Sample if requested
        if args.sample:
            print(f"Sampling {args.sample} rows from training data...")
            if len(train_df) > args.sample:
                train_df = train_df.sample(n=args.sample, random_state=42)
            
            # Also sample test for speed in evaluation
            test_sample_size = int(args.sample * 0.2)
            if len(test_df) > test_sample_size:
                 test_df = test_df.sample(n=test_sample_size, random_state=42)
            print(f"New Train shape: {train_df.shape}")
            print(f"New Test shape: {test_df.shape}")

        # Clean column names for XGBoost
        train_df = clean_column_names(train_df)
        test_df = clean_column_names(test_df)
        
        print("Cleaned Columns:", train_df.columns.tolist())
        # Check for bad ones manually
        for col in train_df.columns:
            if any(c in col for c in ['[', ']', '<', '>']):
                 print(f"BAD COLUMN LEFT: {col}")

        X_train_full, y_train_full, X_test, y_test = prepare_data(train_df, test_df)
        
        # Split a validation set from training for early stopping
        # Ensure we have enough data for split
        if len(X_train_full) > 100:
             X_train, X_val, y_train, y_val = train_test_split(
                X_train_full, y_train_full, test_size=0.1, random_state=42, stratify=y_train_full
            )
        else:
             print("Dataset too small for split, using all for training and validation")
             X_train, y_train = X_train_full, y_train_full
             X_val, y_val = X_train_full, y_train_full
        
        clf = train_model(X_train, y_train, X_val, y_val, use_gpu=use_gpu)
        
        # Save model
        clf.save_model(MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")

        # Save feature list
        print("Saving feature list...")
        feature_list = {
            "features": X_train.columns.tolist(),
            "labels": {"FalsePositive": 0, "BenignPositive": 1, "TruePositive": 2}
        }
        feature_list_path = BASE_DIR / "ml" / "feature_list.json"
        with open(feature_list_path, "w") as f:
            json.dump(feature_list, f)
        print(f"Feature list saved to {feature_list_path}")
        
        if y_test is not None:
            evaluate_model(clf, X_test, y_test)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
