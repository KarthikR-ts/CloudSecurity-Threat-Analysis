#!/usr/bin/env python3
"""
AI-Enhanced Cloud Security Posture Management - Corrected ML Pipeline
Microsoft GUIDE Dataset Preparation (Phases 1-6)
Optimized for 96% Macro-F1 and memory efficiency in Google Colab
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime
from pathlib import Path

# =============================================================================
# SETUP & DIRECTORIES
# =============================================================================
DATA_DIR = Path("/content")
ARTIFACTS_DIR = DATA_DIR / "artifacts"
PLOTS_DIR = ARTIFACTS_DIR / "eda_plots"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("PHASE 1: Schema Ingestion & Data Loading")
print("=" * 70)

# Load pickle files
train_df = pd.read_pickle(DATA_DIR / "train_ready.pkl")
test_df = pd.read_pickle(DATA_DIR / "test_ready.pkl")

print(f"✅ Loaded {len(train_df):,} training rows and {len(test_df):,} testing rows.")

# =============================================================================
# PHASE 2: ADVANCED FEATURE ENGINEERING (PILLAR 2)
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 2 & 4: Security Feature Engineering (Bursts & Frequency)")
print("=" * 70)

def engineer_security_features(df):
    df = df.copy()

    # 1. Normalize Timestamps
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)
    df = df.sort_values('Timestamp')

    # 2. Temporal Features
    df['hour_of_day'] = df['Timestamp'].dt.hour
    df['day_of_week'] = df['Timestamp'].dt.dayofweek
    df['is_night'] = ((df['hour_of_day'] >= 22) | (df['hour_of_day'] <= 6)).astype(int)

    # 3. Alert Bursts (Frequency per Organization per Hour)
    df['hour_bucket'] = df['Timestamp'].dt.floor('H')
    org_hour_counts = df.groupby(['OrgId', 'hour_bucket']).size().reset_index(name='alert_burst_count')
    df = df.merge(org_hour_counts, on=['OrgId', 'hour_bucket'], how='left')

    # 4. Inter-arrival Time (Time between consecutive alerts for same Account)
    # This identifies rapid automated attacks vs slow admin activity
    df['inter_arrival_time'] = df.groupby('AccountObjectId')['Timestamp'].diff().dt.total_seconds().fillna(0)

    # 5. Asset Criticality Proxy
    critical_entities = ['Machine', 'CloudApplication', 'Domain']
    df['is_critical_asset'] = df['EntityType'].isin(critical_entities).astype(int)

    return df.drop(columns=['hour_bucket'])

print("🔧 Engineering features for Train...")
train_df = engineer_security_features(train_df)
print("🔧 Engineering features for Test...")
test_df = engineer_security_features(test_df)

# =============================================================================
# PHASE 5: CORRECTED LABEL ENGINEERING
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 5: Corrected Label Engineering")
print("=" * 70)

# The Microsoft GUIDE dataset uses these specific string labels
FIXED_LABEL_MAP = {
    "FalsePositive": 0,
    "BenignPositive": 1,
    "TruePositive": 2
}

# Preserve original for validation
train_df["IncidentGrade_Original"] = train_df["IncidentGrade"].copy()

# Apply fixed mapping
train_df["IncidentGrade_Encoded"] = train_df["IncidentGrade"].map(FIXED_LABEL_MAP)
test_df["IncidentGrade_Encoded"] = test_df["IncidentGrade"].map(FIXED_LABEL_MAP)

# Drop rows with NaN labels (usually unlabelled data in the raw set)
train_df = train_df.dropna(subset=["IncidentGrade_Encoded"])
train_df["IncidentGrade_Encoded"] = train_df["IncidentGrade_Encoded"].astype(int)

print(f"📋 Label Mapping applied: {FIXED_LABEL_MAP}")
print("\n✅ Final Label Distribution (Train):")
print(train_df["IncidentGrade_Encoded"].value_counts().sort_index())

# =============================================================================
# PHASE 6: ML-READY EXPORT
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 6: ML-Ready Dataset Construction")
print("=" * 70)

# Identify IDs and raw timestamps to exclude from training
EXCLUDE = ['Id', 'IncidentId', 'AlertId', 'Timestamp', 'IncidentGrade',
           'IncidentGrade_Original', 'IncidentGrade_Encoded', 'OrgId']

# Get common features that exist in both sets
INCLUDE = [c for c in train_df.columns if c not in EXCLUDE and c in test_df.columns]

# Ensure high-cardinality strings are excluded if not encoded
high_card_strings = ['MitreTechniques', 'ThreatFamily']
INCLUDE = [c for c in INCLUDE if c not in high_card_strings]

print(f"📊 Final Feature Count: {len(INCLUDE)}")

# Final Datasets
train_ml = train_df[INCLUDE + ["IncidentGrade_Encoded"]]
test_ml = test_df[INCLUDE + ["IncidentGrade_Encoded"]]

# Save as Parquet for Phase 7 (XGBoost Training)
train_ml.to_parquet(ARTIFACTS_DIR / "train_ml_ready.parquet", index=False)
test_ml.to_parquet(ARTIFACTS_DIR / "test_ml_ready.parquet", index=False)

# Save Feature List for RAG/Inference consistency
with open(ARTIFACTS_DIR / "feature_list.json", "w") as f:
    json.dump({"features": INCLUDE, "labels": FIXED_LABEL_MAP}, f)

# =============================================================================
# PHASE 3: SECURITY EDA PLOTS
# =============================================================================
plt.figure(figsize=(10, 6))
sns.countplot(data=train_df, x='IncidentGrade_Encoded', palette='viridis')
plt.title("Incident Triage Distribution (0:FP, 1:BP, 2:TP)")
plt.savefig(PLOTS_DIR / "target_distribution.png")

print(f"\n🚀 PIPELINE COMPLETE!")
print(f"📁 ML-Ready files saved to: {ARTIFACTS_DIR}")
print(f"📈 Triage TPs: {len(train_df[train_df['IncidentGrade_Encoded']==2]):,}")