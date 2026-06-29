# World Cup Match Predictor

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)
[![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20CatBoost%20%7C%20LightGBM-orange)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The World Cup Match Predictor is a sophisticated, end-to-end data science and machine learning suite exclusively dedicated to forecasting the complex outcomes of the FIFA 2026 World Cup. This comprehensive project encapsulates the entirety of the modern machine learning lifecycle. It begins with resilient, automated data acquisition pipelines and advanced web scraping utilities designed to continuously gather, clean, and normalize decades of historical match data, individual player statistics, team performance metrics, and real-time injury reports from disparate global sources.

At its analytical core, the suite leverages a powerful ensemble of state-of-the-art gradient boosting frameworks—specifically XGBoost, CatBoost, and LightGBM. These advanced models are rigorously trained and cross-validated on massive datasets to capture complex, non-linear relationships between team dynamics and match outcomes. The pipeline includes extensive feature engineering, hyperparameter tuning, and automated model evaluation to ensure highly accurate predictive capabilities. This allows the system to not only forecast individual match results but also simulate entire tournament brackets and calculate granular finalist probabilities via Monte Carlo simulations.

All of these complex, computationally intensive analytics are beautifully surfaced through an intuitive, highly interactive Streamlit dashboard. This frontend is securely served by a lightning-fast FastAPI backend, providing seamless and responsive user interactions. Football analysts, enthusiasts, and statisticians can use the platform to dynamically adjust team parameters, explore predictive confidence intervals, and visualize model feature importances, bridging the gap between raw data science and accessible sports analytics.

---

## 📂 Suite Components

This repository contains 4 distinct subsystems, each representing a progressive iteration or module of the prediction system:

### 1. [⚽ Data Scraper](data-scraper/)
A specialized Streamlit scraping utility.
- **Capabilities**: Parses FIFA Elo rankings, squad metrics, Transfermarkt listings, and Wikipedia tables.
- **Output**: Generates clean `.csv` and `.xlsx` team matrices.

### 2. [🔮 Prediction System (v3.0)](predict-system-v3/)
Decoupled match prediction engine featuring NLP-mined injuries and tournament simulations.
- **Backend**: FastAPI server connected to a PostgreSQL database via SQLAlchemy.
- **NLP Engine**: spaCy NER (Named Entity Recognition) to mine football news for squad injuries.
- **ML Engine**: Dual Poisson regression meta-models (XGBoost + CatBoost).

### 3. [🏆 Finalist Predictor (LightGBM)](finalist-predictor-lightgbm/)
Interactive bracket simulation app.
- **ML Engine**: LightGBM classifier calibrated using Platt/Isotonic scaling.
- **Simulation**: Monte Carlo bracket engine (runs 5,000+ simulation pathways to calculate finalist probabilities).
- **Cache**: SQLite cache for FBref, Understat, and Transfermarkt.

### 4. [🖥️ Model Serving Classic (Komma)](model-serving-classic/)
Monolithic streamlit pipeline.
- **Pipeline**: Automated data fetch ➔ feature scaling ➔ XGBoost model training ➔ Streamlit GUI rendering.

### 📊 Subsystem ML Model & Tech Matrix

| Subsystem | Folder | Key Algorithms | Serving Web Tech | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Data Scraper** | `data-scraper/` | BeautifulSoup, Regex | Streamlit | Fetches squad metrics, Elo ranks, wiki data to CSV |
| **Predictor v3** | `predict-system-v3/` | Poisson Regression, XGBoost, CatBoost | FastAPI + Streamlit + SQLite | Simulates matches with mined injury data |
| **Finalist Model** | `finalist-predictor-lightgbm/` | LightGBM, Monte Carlo | Streamlit | 5,000+ simulation path bracket generator |
| **Model serving** | `model-serving-classic/` | XGBoost pipeline | Streamlit | Direct monolithic pipeline from features to UI |

---

## 🏗️ Project Architecture

```
world-cup-match-predictor/
├── LICENSE
├── README.md
│
├── data-scraper/                 # FIFA & player stats web scraper
│   ├── app.py                    # Streamlit control panel
│   ├── data_collector.py         # Scraping executor
│   ├── scrapers/                 # Scraper modules (squad, Elo, wiki)
│   └── exports/                  # Scraped output files (.csv, .xlsx)
│
├── finalist-predictor-lightgbm/  # LightGBM Monte Carlo simulator
│   ├── app.py                    # Streamlit bracket GUI dashboard
│   ├── data_orchestrator.py      # Feature preprocessor
│   ├── ml_pipeline/              # Feature engineering & simulation engine
│   └── scrapers/                 # FBref, Transfermarkt, Understat scrapers
│
├── model-serving-classic/        # Simple monolithic MVP pipeline
│   ├── app.py                    # Classic streamlit interface
│   ├── model_trainer.py          # Local model trainer (XGBoost)
│   └── models/                   # Serialized model pickles
│
└── predict-system-v3/            # Enterprise-grade decoupled predictor
    ├── app.py                    # Streamlit client app
    ├── api/                      # FastAPI endpoint controllers
    ├── database/                 # SQLAlchemy model and session manager
    ├── ml/                       # Advanced match prediction engine
    ├── nlp/                      # spaCy injury news miners
    └── scripts/                  # DB initializers & startup launchers
```

---

## 🛠️ Tech Stack

| Layer | Technology | Detail |
| :--- | :--- | :--- |
| **Backend Engines** | Python 3.11, FastAPI | Rapid, typed REST endpoints |
| **Web Dashboards** | Streamlit | Direct Python UI generation |
| **ML Classifiers** | XGBoost, CatBoost, LightGBM | Gradient boosting ensembles |
| **NLP Miner** | spaCy (Named Entity Recognition) | Information extraction from sports news |
| **Database Storage**| PostgreSQL, SQLite3 | Relational caching and stats tables |
| **Environment** | UV (Python Package Manager) | Fast workspace sync and locked runs |

---

## 🚀 Setup & Installation

This project utilizes the ultra-fast Python package manager **uv**.

### Prerequisites
- **Python 3.11+**
- **uv** (Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`)

### Running the Subsystems

First, clone the repository:
```bash
git clone https://github.com/vemana4/world-cup-match-predictor.git
cd world-cup-match-predictor
```

#### 1. Data Scraper Console
```bash
cd data-scraper
uv sync
uv run streamlit run app.py
```

#### 2. FastAPI + Streamlit Predictor (v3.0)
Ensure database is initialized and spin up the backend:
```bash
cd predict-system-v3
uv sync

# Run database setup
uv run python scripts/init_database.py

# Launch FastAPI backend server
uv run python scripts/run_fastapi.py &

# Launch Streamlit client UI dashboard
uv run streamlit run app.py
```

#### 3. LightGBM Finalist Simulator
```bash
cd finalist-predictor-lightgbm
uv sync
uv run python initialize_data.py
uv run python main.py
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/vemana4">Vemana Hemanth Babu</a>
</p>
