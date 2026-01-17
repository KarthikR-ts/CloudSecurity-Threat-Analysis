
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, f1_score, confusion_matrix, accuracy_score
import json
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path

# =============================================================================
# SETUP
# =============================================================================
BASE_DIR = Path(r"c:\Users\Kartik\Desktop\1st project\el3\CloudSecurity-Threat-Analysis")
DATA_FILE_TRAIN = BASE_DIR / "train_ml_ready.parquet"
DATA_FILE_TEST = BASE_DIR / "test_ml_ready.parquet"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = ARTIFACTS_DIR / "xgboost_model.json"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"

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

def train_model(X_train, y_train, X_val, y_val):
    print("Training XGBoost model...")
    
    # Initialize XGBoost Classifier
    # Using 'hist' tree method for faster training on larger datasets if available
    clf = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,  # 0, 1, 2
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42,
        tree_method='hist', 
        enable_categorical=True,  # Enable native categorical support
        early_stopping_rounds=10
    )
    
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
    
    print(f"Accuracy: {acc:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save metrics
    metrics = {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "classification_report": report
    }
    
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
        
    return metrics

def clean_column_names(df):
    # XGBoost doesn't like some characters in feature names
    import re
    regex = re.compile(r"[\[\]<>]", re.IGNORECASE)
    df.columns = [regex.sub("_", col) if any(x in str(col) for x in set(('[', ']', '<', '>'))) else col for col in df.columns]
    return df


import argparse

def main():
    parser = argparse.ArgumentParser(description="Train XGBoost Model")
    parser.add_argument("--sample", type=int, default=None, help="Number of rows to sample for training")
    args = parser.parse_args()

    try:
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
        
        clf = train_model(X_train, y_train, X_val, y_val)
        
        # Save model
        clf.save_model(MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
        
        if y_test is not None:
            evaluate_model(clf, X_test, y_test)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

