# 🖥️ Model Serving Architecture (Komma)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org) [![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange)](https://xgboost.readthedocs.io) [![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-blue)](https://www.postgresql.org)

A production-style model serving and training pipeline featuring automated data collection, feature preprocessing, XGBoost classification training, and Monte Carlo simulations, connected to a PostgreSQL database.

## 🚀 Key Technologies
- **Machine Learning**: XGBoost, Scikit-learn
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Serving Framework**: Streamlit web GUI dashboard

## 📦 Getting Started & Installation
```bash
# Install dependencies
uv sync

# Ensure PostgreSQL DATABASE_URL env variable is set
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Run model training and serving
uv run streamlit run app.py
```

## 📜 License
This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
