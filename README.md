# World Cup Match Predictor

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)
[![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20CatBoost%20%7C%20LightGBM-orange)](https://github.com/)

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

---

## 🚀 Setup & Installation

To configure and run any component, navigate to its subdirectory and follow its respective setup instructions.

For example, to run the **Data Scraper**:
```bash
cd data-scraper
uv sync
uv run streamlit run app.py
```

To run the **FastAPI + Streamlit Predictor (v3.0)**:
```bash
cd predict-system-v3
uv sync
uv run python scripts/init_database.py
uv run python scripts/run_fastapi.py &
uv run streamlit run app.py
```

---

## 📜 License
This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
