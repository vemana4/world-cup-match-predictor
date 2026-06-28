# 🔮 FIFA 26 Prediction System (v3.0)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org) [![FastAPI Backend](https://img.shields.io/badge/API-FastAPI-green)](https://fastapi.tiangolo.com) [![NLP Engine](https://img.shields.io/badge/NLP-spaCy-blue)](https://spacy.io) [![Streamlit Frontend](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)

A state-of-the-art match-level prediction engine for the FIFA 2026 World Cup. Uses dual-regression Poisson meta-models (XGBoost + CatBoost) to predict goal outcomes, spaCy NLP to monitor injuries from news sources, and Monte Carlo bracket simulations.

## 🚀 Key Technologies
- **Backend**: FastAPI + Uvicorn + PostgreSQL (SQLAlchemy)
- **ML Pipeline**: XGBoost, CatBoost, Scikit-Learn
- **NLP**: spaCy NER (Named Entity Recognition for injury mining)
- **Scheduler**: APScheduler (automated daily scraping heartbeats)

## 📦 Getting Started & Installation
```bash
# Install backend and machine learning dependencies
uv sync

# Initialize database schema and base FIFA rankings
uv run python scripts/init_database.py

# Run the FastAPI server backend
uv run python scripts/run_fastapi.py

# Run the Streamlit dashboard UI
uv run streamlit run app.py --server.port 5000
```

## 📜 License
This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
