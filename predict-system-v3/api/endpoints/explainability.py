from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, ModelPrediction, PredictionExplainability
from api import schemas
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/get_match_explainability/{match_id}", response_model=schemas.ExplainabilityResponse)
async def get_match_explainability(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    Get SHAP/feature importance explainability for a specific prediction.
    Returns top features and human-readable explanation.
    """
    try:
        prediction = db.query(ModelPrediction).filter(
            ModelPrediction.match_id == match_id
        ).order_by(ModelPrediction.prediction_date.desc()).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found for this match")
        
        explainability = db.query(PredictionExplainability).filter(
            PredictionExplainability.prediction_id == prediction.id
        ).first()
        
        if not explainability:
            raise HTTPException(status_code=404, detail="Explainability data not found")
        
        top_features = []
        if explainability.feature_importance:
            sorted_features = sorted(
                explainability.feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:10]
            top_features = [{"feature": k, "importance": v} for k, v in sorted_features]
        
        return schemas.ExplainabilityResponse(
            prediction_id=prediction.id,
            top_features=top_features,
            explanation_text=explainability.top_features_explanation or "No explanation available",
            feature_importance=explainability.feature_importance or {}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving explainability: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving explainability data")

@router.get("/get_fixture_explainability/{fixture_id}", response_model=schemas.ExplainabilityResponse)
async def get_fixture_explainability(
    fixture_id: int,
    db: Session = Depends(get_db)
):
    """
    Get SHAP/feature importance explainability for a specific fixture prediction.
    """
    try:
        prediction = db.query(ModelPrediction).filter(
            ModelPrediction.fixture_id == fixture_id
        ).order_by(ModelPrediction.prediction_date.desc()).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found for this fixture")
        
        explainability = db.query(PredictionExplainability).filter(
            PredictionExplainability.prediction_id == prediction.id
        ).first()
        
        if not explainability:
            raise HTTPException(status_code=404, detail="Explainability data not found")
        
        top_features = []
        if explainability.feature_importance:
            sorted_features = sorted(
                explainability.feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:10]
            top_features = [{"feature": k, "importance": v} for k, v in sorted_features]
        
        return schemas.ExplainabilityResponse(
            prediction_id=prediction.id,
            top_features=top_features,
            explanation_text=explainability.top_features_explanation or "No explanation available",
            feature_importance=explainability.feature_importance or {}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving explainability: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving explainability data")
