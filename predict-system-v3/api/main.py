from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, init_db
from api import schemas
from api.endpoints import predictions, fixtures, tournament, explainability
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FIFA 2026 World Cup Prediction API",
    description="State-of-the-art AI system for predicting FIFA match outcomes with 80%+ target accuracy",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions.router, prefix="/api", tags=["predictions"])
app.include_router(fixtures.router, prefix="/api", tags=["fixtures"])
app.include_router(tournament.router, prefix="/api", tags=["tournament"])
app.include_router(explainability.router, prefix="/api", tags=["explainability"])

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "FIFA 2026 World Cup Prediction API v3.0",
        "status": "operational",
        "features": [
            "Dual-regression goal prediction model",
            "Player-level xG/xA data integration",
            "NLP injury detection",
            "Live betting market analysis",
            "SHAP explainability",
            "Monte Carlo tournament simulation"
        ]
    }

@app.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "version": "3.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
