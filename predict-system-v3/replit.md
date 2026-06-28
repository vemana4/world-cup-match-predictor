# FIFA 2026 World Cup Prediction System v3.0

## Project Overview
State-of-the-art FIFA match prediction system targeting **80%+ accuracy** using:
- Dual-regression goal prediction (predicts home_goals & away_goals)
- Player-level xG/xA data from FBref
- NLP injury detection with spaCy
- Market values from Transfermarkt
- Stacked ensemble ML (XGBoost + CatBoost)

## Architecture
**Decoupled 3-tier system:**
1. FastAPI backend (port 8000) - RESTful API
2. Streamlit frontend (port 5000) - Interactive dashboard
3. APScheduler service - Daily data scraping automation

## Current Status
**MVP Complete** - Core prediction engine operational

### Implemented Features
✅ Database schema (13 tables) with 32 FIFA teams
✅ Dual-regression goal prediction model
✅ Player-level data scrapers (FBref, Transfermarkt)
✅ NLP injury detector (spaCy NER)
✅ Feature engineering (Starting XI aggregates)
✅ Tournament Monte Carlo simulator
✅ Streamlit dashboard with 5 tabs
✅ API endpoints for predictions & explainability
✅ APScheduler with 4 daily jobs

### Pending Enhancements
⚙️ Live betting API integration (The Odds API)
⚙️ Weather/referee contextual scrapers
⚙️ Sentiment analysis (RoBERTa fine-tuning)
⚙️ Tactical keyword extraction
⚙️ Automated model retraining
⚙️ Advanced anomaly detection

## Key Files
- `app.py` - Streamlit frontend
- `api/main.py` - FastAPI application
- `ml/prediction_engine.py` - Core prediction logic
- `database/models.py` - SQLAlchemy schema
- `scheduler/daily_jobs.py` - Automated jobs

## Data Philosophy
**REAL DATA ONLY** - No fake/mock data
Sources: FBref, Transfermarkt, FIFA rankings, news APIs

## How to Use
1. Both workflows auto-start (backend + frontend)
2. Access dashboard at webview
3. Enter teams (e.g., "France" vs "Brazil")
4. Get prediction with goal distributions & probabilities

## Recent Changes
- 2024-01-06: Initialized database with 32 teams & 22 players
- 2024-01-06: Implemented dual-regression model architecture
- 2024-01-06: Created Streamlit UI with goal visualizations
- 2024-01-06: Set up APScheduler with daily scraping jobs
- 2024-01-06: Fixed LightGBM dependency (using XGBoost+CatBoost)

## User Preferences
- Focus on production-grade, scalable architecture
- Emphasis on explainability and trust-building UI
- Real data integration over synthetic placeholders
- 80%+ accuracy target through advanced features

## Project Goals
Build comprehensive FIFA prediction system following 7-phase architecture plan targeting professional-level accuracy through player-level data, NLP context, and advanced ML techniques.
