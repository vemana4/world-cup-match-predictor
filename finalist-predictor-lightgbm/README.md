# 🏆 FIFA 2026 Finalist Predictor

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org) [![LightGBM Classifier](https://img.shields.io/badge/ML-LightGBM-blue)](https://github.com/microsoft/LightGBM) [![Streamlit Dashboard](https://img.shields.io/badge/UI-Streamlit-red)](https://streamlit.io)

An interactive tournament bracket simulator that employs LightGBM classifier models trained on 20+ years of historical match outcomes, squad values, and tactical metrics to predict the probabilities of teams reaching the World Cup finals.

## 🚀 Key Technologies
- **Machine Learning**: LightGBM, Scikit-learn (Platt/Isotonic probability calibration)
- **Simulation**: Monte Carlo tournament engine (5000+ brackets)
- **Caching**: Local SQLite request cache for FBref, Understat, and Transfermarkt

## 📦 Getting Started & Installation
```bash
# Install dependencies
uv sync

# Initialize cache and download historical data
uv run python initialize_data.py

# Run the Streamlit dashboard
uv run streamlit run app.py --server.port 5000
```

## 📜 License
This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
