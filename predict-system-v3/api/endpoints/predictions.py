from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from api import schemas
from ml.prediction_engine import PredictionEngine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

prediction_engine = None

def get_prediction_engine():
    global prediction_engine
    if prediction_engine is None:
        prediction_engine = PredictionEngine()
    return prediction_engine

@router.post("/predict", response_model=schemas.PredictionResponse)
async def predict_match(
    request: schemas.MatchPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict match outcome using dual-regression goal prediction model.
    Returns predicted goals for both teams and Win/Draw/Loss probabilities.
    """
    try:
        engine = get_prediction_engine()
        prediction = engine.predict_match(
            home_team=request.home_team_name,
            away_team=request.away_team_name,
            db=db,
            scheduled_date=request.scheduled_date,
            competition=request.competition,
            venue=request.venue
        )
        return prediction
    except ValueError as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction")

@router.get("/predict/{match_id}", response_model=schemas.PredictionResponse)
async def get_match_prediction(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Get prediction for a specific match by ID.
    """
    try:
        engine = get_prediction_engine()
        prediction = engine.get_prediction_by_match_id(match_id, db)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        return prediction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/predict/fixture/{fixture_id}", response_model=schemas.PredictionResponse)
async def get_fixture_prediction(
    fixture_id: int,
    db: Session = Depends(get_db)
):
    """
    Get prediction for a specific live fixture by ID.
    """
    try:
        engine = get_prediction_engine()
        prediction = engine.get_prediction_by_fixture_id(fixture_id, db)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        return prediction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving fixture prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
