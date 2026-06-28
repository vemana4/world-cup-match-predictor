"""
ML Model Training Module for FIFA Match Prediction
Uses XGBoost for multiclass classification (Win/Draw/Loss)
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, log_loss, confusion_matrix
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import pickle
import json
from datetime import datetime
from typing import Tuple, Dict
import os


class FIFAMatchPredictor:
    """XGBoost-based match outcome predictor"""
    
    def __init__(self, model_path: str = "models/xgboost_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_columns = None
        self.is_trained = False
        
    def train(self, train_df: pd.DataFrame, feature_columns: list, 
              target_column: str = 'target') -> Dict:
        """
        Train XGBoost classifier on historical match data
        
        Target encoding:
        0 = Home Win
        1 = Draw
        2 = Away Win
        """
        print("\n🎯 Training XGBoost match prediction model...\n")
        
        self.feature_columns = feature_columns
        
        # Prepare training data
        X = train_df[feature_columns].fillna(0)
        y = train_df[target_column]
        
        # Check if all classes are present for stratification
        unique_classes = y.nunique()
        stratify_param = y if unique_classes >= 2 else None
        
        # Split for validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.15, random_state=42, stratify=stratify_param
        )
        
        print(f"📊 Training set: {len(X_train)} matches")
        print(f"📊 Validation set: {len(X_val)} matches")
        print(f"📊 Class distribution:")
        print(f"   Home Win: {(y_train == 0).sum()} ({(y_train == 0).mean()*100:.1f}%)")
        print(f"   Draw: {(y_train == 1).sum()} ({(y_train == 1).mean()*100:.1f}%)")
        print(f"   Away Win: {(y_train == 2).sum()} ({(y_train == 2).mean()*100:.1f}%)")
        
        # Configure XGBoost for multiclass classification
        self.model = xgb.XGBClassifier(
            objective='multi:softmax',  # Multiclass classification (returns class labels)
            num_class=3,
            max_depth=6,
            learning_rate=0.1,
            n_estimators=300,
            subsample=0.9,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.05,
            reg_lambda=1.0,
            random_state=42,
            eval_metric='mlogloss'
        )
        
        # Train with early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        self.is_trained = True
        
        # Evaluate
        metrics = self._evaluate(X_train, y_train, X_val, y_val)
        
        # Save model
        self._save_model()
        
        print("\n✅ Model training complete!")
        
        return metrics
    
    def _evaluate(self, X_train, y_train, X_val, y_val) -> Dict:
        """Evaluate model performance"""
        # Training predictions
        train_pred = self.model.predict(X_train)
        train_pred = np.ravel(train_pred).astype(int)  # Ensure 1D array of integers
        train_acc = accuracy_score(y_train, train_pred)
        
        # Validation predictions
        val_pred = self.model.predict(X_val)
        val_pred = np.ravel(val_pred).astype(int)  # Ensure 1D array of integers
        val_acc = accuracy_score(y_val, val_pred)
        
        # Probability predictions
        val_proba = self.model.predict_proba(X_val)
        val_logloss = log_loss(y_val, val_proba, labels=[0, 1, 2])
        
        print(f"\n📈 Model Performance:")
        print(f"   Training Accuracy: {train_acc*100:.2f}%")
        print(f"   Validation Accuracy: {val_acc*100:.2f}%")
        print(f"   Validation Log Loss: {val_logloss:.4f}")
        
        print(f"\n📊 Validation Classification Report:")
        print(classification_report(y_val, val_pred, 
                                   target_names=['Home Win', 'Draw', 'Away Win'],
                                   labels=[0, 1, 2],
                                   zero_division=0))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔝 Top 10 Most Important Features:")
        print(feature_importance.head(10).to_string(index=False))
        
        metrics = {
            'train_accuracy': float(train_acc),
            'val_accuracy': float(val_acc),
            'val_logloss': float(val_logloss),
            'feature_importance': feature_importance.to_dict('records'),
            'trained_at': datetime.now().isoformat()
        }
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict match outcomes
        
        Returns:
        - predictions: array of predicted classes (0, 1, 2)
        - probabilities: array of shape (n_samples, 3) with [prob_home, prob_draw, prob_away]
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load existing model.")
        
        X_prepared = X[self.feature_columns].fillna(0)
        
        predictions = self.model.predict(X_prepared)
        probabilities = self.model.predict_proba(X_prepared)
        
        return predictions, probabilities
    
    def predict_match(self, home_team: str, away_team: str, features: pd.DataFrame) -> Dict:
        """
        Predict single match with detailed output
        
        Returns dict with:
        - home_win_prob
        - draw_prob
        - away_win_prob
        - predicted_outcome
        - confidence
        """
        predictions, probabilities = self.predict(features)
        
        prob_home, prob_draw, prob_away = probabilities[0]
        predicted_class = predictions[0]
        
        outcome_map = {0: 'Home Win', 1: 'Draw', 2: 'Away Win'}
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prob_home_win': float(prob_home),
            'prob_draw': float(prob_draw),
            'prob_away_win': float(prob_away),
            'predicted_outcome': outcome_map[predicted_class],
            'confidence': float(probabilities[0].max()),
            'prediction_time': datetime.now().isoformat()
        }
    
    def _save_model(self):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'trained_at': datetime.now().isoformat()
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Model saved to {self.model_path}")
    
    def load_model(self):
        """Load pre-trained model from disk"""
        if not os.path.exists(self.model_path):
            print(f"⚠️  Model file not found: {self.model_path}")
            return False
        
        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = True
        
        print(f"✅ Model loaded from {self.model_path}")
        print(f"   Trained at: {model_data['trained_at']}")
        
        return True


class AnomalyDetector:
    """Detect anomalous matches using IsolationForest"""
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=200,
            max_samples='auto',
            random_state=42
        )
        self.is_trained = False
    
    def train(self, df: pd.DataFrame, anomaly_features: list):
        """Train anomaly detector on match data"""
        print(f"\n🔍 Training anomaly detector...")
        
        X = df[anomaly_features].fillna(0)
        self.model.fit(X)
        self.is_trained = True
        
        # Get anomaly scores on training data
        scores = self.model.score_samples(X)
        anomalies = self.model.predict(X)
        
        n_anomalies = (anomalies == -1).sum()
        print(f"   Detected {n_anomalies} anomalous matches ({n_anomalies/len(df)*100:.2f}%)")
        
        return scores, anomalies
    
    def detect(self, df: pd.DataFrame, anomaly_features: list) -> np.ndarray:
        """
        Detect anomalies in new data
        
        Returns:
        - anomaly_score: normalized 0-1 where 1 = normal, 0 = anomalous
        """
        if not self.is_trained:
            raise ValueError("Anomaly detector not trained")
        
        X = df[anomaly_features].fillna(0)
        scores = self.model.score_samples(X)
        
        # Normalize to 0-1 range (1 = normal, 0 = anomalous)
        min_score = scores.min()
        max_score = scores.max()
        normalized_scores = (scores - min_score) / (max_score - min_score)
        
        return normalized_scores
    
    def get_anomaly_features(self) -> list:
        """Return features used for anomaly detection"""
        return [
            'rank_difference',
            'points_difference',
            'goal_difference',
            'possession_diff'
        ]


if __name__ == "__main__":
    # Test model training
    from data_collection import collect_all_data
    from preprocessing import load_and_preprocess
    
    print("🚀 Testing FIFA Match Prediction System\n")
    
    # Collect data
    data = collect_all_data()
    
    # Preprocess
    train_df, test_df, preprocessor = load_and_preprocess(
        data['matches'], 
        data['rankings']
    )
    
    # Train model
    predictor = FIFAMatchPredictor()
    metrics = predictor.train(train_df, preprocessor.get_feature_columns())
    
    # Test prediction
    test_features = preprocessor.prepare_prediction_features(
        'Argentina', 'Brazil', data['rankings']
    )
    prediction = predictor.predict_match('Argentina', 'Brazil', test_features)
    
    print(f"\n🎯 Sample Prediction: Argentina vs Brazil")
    print(f"   Home Win: {prediction['prob_home_win']*100:.1f}%")
    print(f"   Draw: {prediction['prob_draw']*100:.1f}%")
    print(f"   Away Win: {prediction['prob_away_win']*100:.1f}%")
    print(f"   Predicted: {prediction['predicted_outcome']}")
    
    # Train anomaly detector
    anomaly_detector = AnomalyDetector()
    anomaly_features = anomaly_detector.get_anomaly_features()
    anomaly_detector.train(train_df, anomaly_features)
    
    print("\n✅ All systems operational!")
