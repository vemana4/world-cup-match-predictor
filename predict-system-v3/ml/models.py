import numpy as np
import xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.linear_model import PoissonRegressor, LogisticRegression
from sklearn.ensemble import StackingRegressor
import logging

logger = logging.getLogger(__name__)

class GoalPredictionModel:
    """
    Dual regression model predicting home_goals and away_goals.
    Uses stacked ensemble with XGBoost and CatBoost.
    """
    
    def __init__(self):
        self.home_goals_model = None
        self.away_goals_model = None
        self.is_trained = False
        self._initialize_models()
        logger.info("GoalPredictionModel initialized")
    
    def _initialize_models(self):
        """
        Initialize stacked ensemble models for goal prediction.
        """
        base_estimators_home = [
            ('xgb', xgb.XGBRegressor(
                objective='count:poisson',
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )),
            ('catboost', CatBoostRegressor(
                iterations=100,
                depth=5,
                learning_rate=0.1,
                verbose=False,
                random_state=42
            ))
        ]
        
        base_estimators_away = [
            ('xgb', xgb.XGBRegressor(
                objective='count:poisson',
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )),
            ('catboost', CatBoostRegressor(
                iterations=100,
                depth=5,
                learning_rate=0.1,
                verbose=False,
                random_state=42
            ))
        ]
        
        self.home_goals_model = StackingRegressor(
            estimators=base_estimators_home,
            final_estimator=PoissonRegressor(max_iter=300),
            cv=5
        )
        
        self.away_goals_model = StackingRegressor(
            estimators=base_estimators_away,
            final_estimator=PoissonRegressor(max_iter=300),
            cv=5
        )
    
    def train(self, X_train, y_home_goals, y_away_goals):
        """
        Train both home and away goal prediction models.
        """
        logger.info("Training home goals model...")
        self.home_goals_model.fit(X_train, y_home_goals)
        
        logger.info("Training away goals model...")
        self.away_goals_model.fit(X_train, y_away_goals)
        
        self.is_trained = True
        logger.info("Goal prediction models trained successfully")
    
    def predict_goals(self, features: dict):
        """
        Predict home and away goals for a match.
        If models aren't trained, use baseline heuristic.
        """
        if not self.is_trained:
            return self._baseline_prediction(features)
        
        X = self._features_to_array(features)
        home_goals = max(0, self.home_goals_model.predict(X)[0])
        away_goals = max(0, self.away_goals_model.predict(X)[0])
        
        return home_goals, away_goals
    
    def _baseline_prediction(self, features: dict):
        """
        Baseline prediction when models aren't trained.
        Uses FIFA rankings and historical averages.
        """
        base_home = 1.5
        base_away = 1.2
        
        rank_diff = features.get('rank_difference', 0)
        home_adjustment = rank_diff * 0.01
        
        home_goals = max(0.1, base_home + home_adjustment)
        away_goals = max(0.1, base_away - home_adjustment)
        
        return home_goals, away_goals
    
    def _features_to_array(self, features: dict):
        """
        Convert feature dictionary to numpy array for prediction.
        """
        feature_list = [
            features.get('rank_difference', 0),
            features.get('points_difference', 0),
            features.get('home_form', 0),
            features.get('away_form', 0),
            features.get('starting_xi_market_value', 0),
            features.get('starting_xi_avg_xg', 0),
            features.get('key_player_injury_penalty', 0),
            features.get('home_win_ratio', 0.5),
            features.get('away_win_ratio', 0.5)
        ]
        return np.array([feature_list])
