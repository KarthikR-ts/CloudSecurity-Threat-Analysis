# Cloud Sentinel - AI-Powered Security Incident Triage

<div align="center">

**An intelligent cloud security platform that combines ML-based alert classification with RAG-powered remediation guidance.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange.svg)](https://xgboost.readthedocs.io)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [ML Model](#ml-model)
- [RAG Pipeline](#rag-pipeline)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Cloud Sentinel is an enterprise-grade security operations platform designed to help SOC (Security Operations Center) analysts efficiently triage and respond to cloud security alerts. The platform addresses the critical challenge of **alert fatigue** by automatically classifying alerts into:

- **True Positives (TP)**: Genuine security threats requiring immediate action
- **False Positives (FP)**: Benign activities incorrectly flagged as threats  
- **Benign Positives (BP)**: Known safe activities that triggered alerts

By leveraging machine learning and AI-powered knowledge retrieval, Cloud Sentinel reduces Mean Time to Resolution (MTTR) by up to **40%** while maintaining high accuracy in threat detection.

---

## Features

### ML-Powered Classification
- **XGBoost Model** trained on 500K+ real-world security alerts
- **3-class classification**: True Positive, False Positive, Benign Positive
- **SHAP Explainability**: Understand why each prediction was made
- **Macro F1 Score**: 82.1% accuracy

### RAG-Powered Remediation
- **Vector Database**: Pinecone with 868+ security documents
- **Knowledge Sources**: MITRE ATT&CK, CIS Benchmarks, Azure Policies
- **AI Advisor**: Gemini-powered contextual remediation guidance
- **Auto-Fix Scripts**: Generate Azure CLI/Terraform remediation code

### Real-Time Dashboard
- **Live Metrics**: Total alerts, TP/FP/BP breakdown, MTTR
- **Incident Table**: Sortable, filterable incident list
- **Alert Volume Chart**: 24-hour trend visualization
- **System Health**: Pipeline status monitoring

### Incident Simulation
- **Traffic Simulator**: Generate realistic security incidents
- **Live Updates**: Dashboard refreshes every 3 seconds
- **Demo Mode**: Perfect for presentations and testing

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLOUD SENTINEL PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌─────────────────────────────────────────────────┐   │
│  │ DATA SOURCES │     │              CORE PLATFORM                       │   │
│  ├──────────────┤     │  ┌─────────────────────────────────────────┐    │   │
│  │Azure Sentinel│────►│  │           FastAPI Backend               │    │   │
│  │AWS CloudTrail│     │  │         (Python 3.10+)                  │    │   │
│  │GCP Security  │     │  └─────────────────────────────────────────┘    │   │
│  └──────────────┘     │       │                    │                     │   │
│                       │       ▼                    ▼                     │   │
│                       │  ┌──────────┐      ┌─────────────────┐          │   │
│                       │  │ XGBoost  │      │  RAG Pipeline   │          │   │
│                       │  │ ML Model │      │  ┌───────────┐  │          │   │
│                       │  │          │      │  │ Pinecone  │  │          │   │
│                       │  │ TP/FP/BP │      │  │ Vector DB │  │          │   │
│                       │  │ Classify │      │  └───────────┘  │          │   │
│                       │  │          │      │  ┌───────────┐  │          │   │
│                       │  │  + SHAP  │      │  │ Gemini    │  │          │   │
│                       │  │ Explain  │      │  │ LLM       │  │          │   │
│                       │  └──────────┘      │  └───────────┘  │          │   │
│                       │                    └─────────────────┘          │   │
│                       │       │                    │                     │   │
│                       │       ▼                    ▼                     │   │
│                       │  ┌─────────────────────────────────────────┐    │   │
│                       │  │      PostgreSQL / Supabase              │    │   │
│                       │  └─────────────────────────────────────────┘    │   │
│                       └─────────────────────────────────────────────────┘   │
│                                          │                                   │
│                                          ▼                                   │
│                       ┌─────────────────────────────────────────────────┐   │
│                       │             Next.js Dashboard                    │   │
│                       │    (React 18 + TypeScript + Tailwind CSS)       │   │
│                       └─────────────────────────────────────────────────┘   │
│                                          │                                   │
│                       ┌──────────────────┼──────────────────┐               │
│                       ▼                  ▼                  ▼               │
│               ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│               │ Auto-Fix     │  │    SHAP      │  │  Real-time   │         │
│               │ Scripts      │  │ Explanations │  │   Alerts     │         │
│               └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async REST API |
| **XGBoost** | Gradient boosting ML model |
| **SHAP** | Model explainability |
| **Sentence Transformers** | Text embeddings (all-MiniLM-L6-v2) |
| **Pinecone** | Vector database for RAG |
| **Google Gemini** | LLM for advice generation |
| **Supabase** | PostgreSQL + Auth |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React framework with App Router |
| **TypeScript** | Type-safe development |
| **Tailwind CSS** | Utility-first styling |
| **Recharts** | Data visualization |
| **Lucide Icons** | UI iconography |

### ML/Data
| Technology | Purpose |
|------------|---------|
| **Pandas** | Data manipulation |
| **NumPy** | Numerical computing |
| **Scikit-learn** | ML utilities |
| **Parquet** | Efficient data storage |

---

## Project Structure

```
CloudSecurity-Threat-Analysis/
│
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── routers/               # API endpoints
│   │   │   ├── auth.py            # Authentication
│   │   │   ├── dashboard.py       # Dashboard data
│   │   │   ├── incidents.py       # Incident management
│   │   │   ├── ml.py              # ML endpoints
│   │   │   ├── predict.py         # Prediction + SHAP
│   │   │   └── rag.py             # RAG search + advice
│   │   ├── rag/                   # RAG Pipeline
│   │   │   ├── embeddings.py      # Text embeddings
│   │   │   ├── rag_pipeline.py    # LLM integration
│   │   │   └── vector_db.py       # Pinecone client
│   │   ├── auth.py                # Auth utilities
│   │   └── main.py                # FastAPI app
│   ├── scripts/                   # Utility scripts
│   │   ├── ingest_data.py         # Load knowledge base
│   │   ├── init_pinecone.py       # Create vector index
│   │   └── simulate_traffic.py    # Generate test incidents
│   ├── .env                       # Environment variables
│   └── requirements.txt           # Python dependencies
│
├── dashboard/                     # Next.js Frontend
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   │   ├── dashboard/
│   │   │   │   ├── enterprise/    # Main dashboard
│   │   │   │   └── incidents/     # Incident details
│   │   │   └── page.tsx           # Landing page
│   │   ├── components/            # React components
│   │   │   ├── dashboard/         # Dashboard widgets
│   │   │   ├── layout/            # Header, Sidebar
│   │   │   └── ui/                # Reusable UI
│   │   └── lib/                   # Utilities
│   │       ├── api.ts             # Backend API client
│   │       └── mock-data.ts       # Sample data
│   ├── package.json
│   └── tailwind.config.ts
│
├── ml/                            # ML Training & Artifacts
│   ├── train_xgboost.py           # Local training script
│   ├── train_xgboost_colab.py     # Colab training script
│   └── feature_list.json          # Model features
│
├── artifacts/                     # Model artifacts
│   ├── xgboost_model.json         # Trained model
│   └── metrics.json               # Evaluation metrics
│
├── .gitignore
└── README.md                      # This file
```

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/CloudSecurity-Threat-Analysis.git
cd CloudSecurity-Threat-Analysis
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see Configuration section)
cp .env.example .env
```

### 3. Frontend Setup
```bash
cd dashboard

# Install dependencies
npm install
```

### 4. Initialize Vector Database
```bash
cd backend

# Create Pinecone index
python scripts/init_pinecone.py

# Load knowledge base
python scripts/ingest_data.py
```

---

## Configuration

Create a `.env` file in the `backend/` directory:

```env
# Supabase (Database & Auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Pinecone (Vector Database)
PINECONE_API_KEY=your-pinecone-api-key

# Google Gemini (LLM)
GEMINI_API_KEY=your-gemini-api-key
```

### Getting API Keys

| Service | How to Get |
|---------|------------|
| **Supabase** | [supabase.com](https://supabase.com) → Create project → Settings → API |
| **Pinecone** | [pinecone.io](https://pinecone.io) → Create account → API Keys |
| **Gemini** | [aistudio.google.com](https://aistudio.google.com) → Get API Key |

---

## Usage

### Start Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd dashboard
npm run dev
```

### Access Dashboard
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Run Traffic Simulator (Optional)
```bash
cd backend
python scripts/simulate_traffic.py
```

---

## API Documentation

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### Prediction
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict/predict` | Classify an incident |
| POST | `/predict/explain` | Get SHAP explanation |

#### RAG
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rag/search` | Search knowledge base |
| POST | `/rag/ask` | Get AI remediation advice |
| POST | `/rag/fix` | Generate auto-fix script |
| GET | `/rag/status` | Check RAG system status |

#### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/incidents/` | List all incidents |
| POST | `/incidents/create` | Create new incident |
| GET | `/incidents/{id}` | Get incident details |

### Example: Classify Incident
```bash
curl -X POST http://localhost:8000/api/predict/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "Category": "Execution",
      "alert_burst_count": 50,
      "hour_of_day": 2,
      "Severity": "High"
    }
  }'
```

### Example: Get Remediation Advice
```bash
curl -X POST http://localhost:8000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to remediate suspicious PowerShell execution?",
    "top_k": 5
  }'
```

---

## ML Model

### Model Details
- **Algorithm**: XGBoost Classifier
- **Task**: Multi-class classification (TP, FP, BP)
- **Training Data**: 500K+ Azure Sentinel alerts
- **Features**: 15+ engineered features

### Performance Metrics
| Metric | Value |
|--------|-------|
| Accuracy | 82.99% |
| Macro F1 | 82.10% |
| Macro Precision | 82.11% |
| Macro Recall | 82.33% |

### Feature Importance (Top 5)
1. `alert_burst_count` - Number of alerts in burst
2. `hour_of_day` - When the alert occurred
3. `Category` - MITRE ATT&CK tactic
4. `inter_arrival_time` - Time between alerts
5. `Severity` - Alert severity level

---

## RAG Pipeline

### Knowledge Base Statistics
| Source | Documents |
|--------|-----------|
| MITRE ATT&CK | 835 techniques |
| CIS Benchmarks | 15 controls |
| Azure Policies | 18 policies |
| **Total** | **868 documents** |

### Pipeline Flow
1. **Query Embedding**: Convert user query to vector (all-MiniLM-L6-v2)
2. **Similarity Search**: Find top-k relevant documents (Pinecone)
3. **Context Assembly**: Build prompt with retrieved context
4. **LLM Generation**: Generate advice using Gemini
5. **Response**: Return advice with source citations

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
