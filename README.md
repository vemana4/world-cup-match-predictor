# World Cup Match Predictor

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)
[![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20CatBoost%20%7C%20LightGBM-orange)](https://github.com/)

The World Cup Match Predictor is an end-to-end data science and machine learning suite dedicated to forecasting the outcomes of the FIFA 2026 World Cup. This comprehensive project encompasses the entire machine learning lifecycle, starting from automated data acquisition and web scraping tools to gather historical match data, player statistics, and team performance metrics. At its core, the suite employs powerful gradient boosting frameworks—including XGBoost, CatBoost, and LightGBM—to train highly accurate predictive models capable of forecasting match results, simulating tournament brackets, and estimating finalist probabilities. All of these complex analytics are surfaced through an intuitive, interactive Streamlit dashboard served by a high-performance FastAPI backend, allowing users to explore predictions and model confidence dynamically.

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
