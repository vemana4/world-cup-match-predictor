import numpy as np
import pandas as pd
from datetime import datetime
from scipy.stats import poisson
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from database import Team, ModelPrediction, PredictionExplainability
from ml.feature_engineering import FeatureEngineer
from ml.models import GoalPredictionModel
import logging

logger = logging.getLogger(__name__)

class PredictionEngine:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.goal_model = GoalPredictionModel()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.model_version = "v3.0_dual_regression"
        logger.info("PredictionEngine initialized")
    
    def predict_match(
        self,
        home_team: str,
        away_team: str,
        db: Session,
        scheduled_date: datetime = None,
        competition: str = "Friendly",
        venue: str = None
    ):
        """
        Predict match outcome using dual-regression goal prediction.
        Returns predicted goals and Win/Draw/Loss probabilities.
        """
        from api.schemas import PredictionResponse
        
        home_team_obj = db.query(Team).filter(Team.name == home_team).first()
        away_team_obj = db.query(Team).filter(Team.name == away_team).first()
        
        if not home_team_obj or not away_team_obj:
            raise ValueError(f"Teams not found in database: {home_team} or {away_team}")
        
        features = self.feature_engineer.engineer_features(
            home_team_id=home_team_obj.id,
            away_team_id=away_team_obj.id,
            db=db,
            scheduled_date=scheduled_date or datetime.utcnow()
        )
        
        pred_home_goals, pred_away_goals = self.goal_model.predict_goals(features)
        
        win_prob, draw_prob, loss_prob = self._calculate_outcome_probabilities(
            pred_home_goals, pred_away_goals
        )
        
        most_likely_score = self._find_most_likely_score(pred_home_goals, pred_away_goals)
        
        confidence = self._calculate_confidence(win_prob, draw_prob, loss_prob)
        
        anomaly_score = self._calculate_anomaly_score(features)
        is_anomaly = anomaly_score > 0.7
        
        prediction_data = PredictionResponse(
            home_team=home_team,
            away_team=away_team,
            predicted_home_goals=round(pred_home_goals, 2),
            predicted_away_goals=round(pred_away_goals, 2),
            home_win_prob=round(win_prob, 3),
            draw_prob=round(draw_prob, 3),
            away_win_prob=round(loss_prob, 3),
            most_likely_score=most_likely_score,
            confidence_score=round(confidence, 3),
            anomaly_score=round(anomaly_score, 3) if anomaly_score else None,
            is_anomaly=is_anomaly,
            prediction_date=datetime.utcnow(),
            model_version=self.model_version
        )
        
        self._save_prediction_to_db(prediction_data, features, db)
        
        return prediction_data
    
    def _calculate_outcome_probabilities(self, home_goals: float, away_goals: float, n_simulations: int = 10000):
        """
        Calculate Win/Draw/Loss probabilities using Monte Carlo simulation with Poisson distributions.
        """
        home_samples = np.random.poisson(home_goals, n_simulations)
        away_samples = np.random.poisson(away_goals, n_simulations)
        
        wins = np.sum(home_samples > away_samples) / n_simulations
        draws = np.sum(home_samples == away_samples) / n_simulations
        losses = np.sum(home_samples < away_samples) / n_simulations
        
        return wins, draws, losses
    
    def _find_most_likely_score(self, home_goals: float, away_goals: float):
        """
        Find the most likely exact score using Poisson distributions.
        """
        max_goals = 6
        max_prob = 0
        most_likely = "0-0"
        
        for h in range(max_goals):
            for a in range(max_goals):
                prob = poisson.pmf(h, home_goals) * poisson.pmf(a, away_goals)
                if prob > max_prob:
                    max_prob = prob
                    most_likely = f"{h}-{a}"
        
        return most_likely
    
    def _calculate_confidence(self, win_prob: float, draw_prob: float, loss_prob: float):
        """
        Calculate confidence based on how clear the prediction is.
        Higher when one outcome dominates.
        """
        max_prob = max(win_prob, draw_prob, loss_prob)
        entropy = -(win_prob * np.log(win_prob + 1e-10) +
                   draw_prob * np.log(draw_prob + 1e-10) +
                   loss_prob * np.log(loss_prob + 1e-10))
        max_entropy = -np.log(1/3)
        confidence = 1 - (entropy / max_entropy)
        return max_prob * confidence
    
    def _calculate_anomaly_score(self, features: dict):
        """
        Calculate anomaly score (placeholder for betting-based anomaly detection).
        """
        return 0.0
    
    def _save_prediction_to_db(self, prediction_data, features: dict, db: Session):
        """
        Save prediction and explainability to database.
        """
        try:
            prediction_record = ModelPrediction(
                model_version=prediction_data.model_version,
                prediction_type="dual_regression_goals",
                predicted_home_goals=prediction_data.predicted_home_goals,
                predicted_away_goals=prediction_data.predicted_away_goals,
                home_win_prob=prediction_data.home_win_prob,
                draw_prob=prediction_data.draw_prob,
                away_win_prob=prediction_data.away_win_prob,
                most_likely_score=prediction_data.most_likely_score,
                confidence_score=prediction_data.confidence_score,
                anomaly_score=prediction_data.anomaly_score,
                is_anomaly=prediction_data.is_anomaly,
                prediction_date=prediction_data.prediction_date
            )
            db.add(prediction_record)
            db.commit()
            db.refresh(prediction_record)
            
            explanation_text = self._generate_explanation_text(features, prediction_data)
            
            explainability_record = PredictionExplainability(
                prediction_id=prediction_record.id,
                feature_importance=features,
                top_features_explanation=explanation_text
            )
            db.add(explainability_record)
            db.commit()
            
            logger.info(f"Saved prediction {prediction_record.id} to database")
        except Exception as e:
            logger.error(f"Error saving prediction to database: {e}")
            db.rollback()
    
    def _generate_explanation_text(self, features: dict, prediction_data):
        """
        Generate human-readable explanation of prediction.
        """
        home_team = prediction_data.home_team
        away_team = prediction_data.away_team
        win_prob = prediction_data.home_win_prob * 100
        
        explanation = f"{home_team} has a {win_prob:.0f}% win chance because: "
        
        feature_contributions = []
        if features.get('rank_difference', 0) > 0:
            feature_contributions.append(f"rank_difference=+{features['rank_difference']:.0f}")
        if features.get('starting_xi_market_value', 0) > 0:
            feature_contributions.append(f"starting_xi_market_value=+{features['starting_xi_market_value']:.0f}M")
        if features.get('key_player_injury_penalty', 0) < 0:
            feature_contributions.append(f"key_player_injury={features['key_player_injury_penalty']:.0f}")
        
        explanation += ", ".join(feature_contributions) if feature_contributions else "balanced team stats"
        
        return explanation
    
    def get_prediction_by_match_id(self, match_id: int, db: Session):
        """
        Retrieve existing prediction for a match.
        """
        prediction = db.query(ModelPrediction).filter(
            ModelPrediction.match_id == match_id
        ).order_by(ModelPrediction.prediction_date.desc()).first()
        return prediction
    
    def get_prediction_by_fixture_id(self, fixture_id: int, db: Session):
        """
        Retrieve existing prediction for a fixture.
        """
        prediction = db.query(ModelPrediction).filter(
            ModelPrediction.fixture_id == fixture_id
        ).order_by(ModelPrediction.prediction_date.desc()).first()
        return prediction
