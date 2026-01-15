# AI-Enhanced Cloud Security Threat Analysis

This project implements an AI-enhanced Cloud Security Posture Management (CSPM) pipeline using the Microsoft GUIDE dataset. It focuses on preparing security logs for machine learning, engineering advanced security features, and optimizing for high-performance triage (Targeting 96% Macro-F1).

## 🚀 Overview

The pipeline processes raw security alert data to identify "True Positives" (TP), "False Positives" (FP), and "Benign Positives" (BP). It automates feature engineering, temporal analysis, and data preparation for training robust ML models like XGBoost.

## 🛠 Features

- **Schema Ingestion**: Loading and parsing complex security log datasets.
- **Advanced Feature Engineering**:
  - **Temporal Analysis**: Hour of day, day of week, and night-time activity detection.
  - **Alert Bursts**: Frequency-based analysis per organization/hour to detect automated attacks.
  - **Inter-arrival Time**: Measuring velocity between consecutive alerts for the same account.
  - **Asset Criticality**: Identifying high-value entities (Machines, Cloud Apps, Domains).
- **Label Engineering**: Standardizing triage grades (FP: 0, BP: 1, TP: 2).
- **ML-Ready Export**: Generating high-efficiency Parquet files for training.

## 📁 Project Structure

- `cspm_pipeline_parquet.py`: Main processing script for feature engineering and data preparation.
- `data_dictionary.md`: Detailed breakdown of dataset columns and types.
- `feature_list.json`: Metadata about selected features and label mappings.
- `dataset_statistics.json`: Summary statistics of the processed data.
- `leakage_report.json`: Verification report to ensure no data leakage between train/test sets.

## 📊 Dataset Summary

The pipeline is designed for the Microsoft GUIDE Dataset, which includes:
- **730k+ Unique IDs**
- **5.7k+ Organizations**
- **1.2M+ Alerts**
- High-cardinality features like `MitreTechniques`, `ThreatFamily`, and `DetectorId`.

## ⚙️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/[your-username]/CloudSecurity-Threat-Analysis.git
   cd CloudSecurity-Threat-Analysis
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the pipeline**:
   ```bash
   python cspm_pipeline_parquet.py
   ```

## 📈 Future Work

- Implementation of Phase 7: XGBoost Model Training.
- Integration with RAG (Retrieval-Augmented Generation) for incident explanation.
- Real-time alert stream processing.

## ⚖️ License

[Specify License, e.g., MIT]
