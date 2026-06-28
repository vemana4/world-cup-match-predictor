"""
Data Preprocessing and Feature Engineering Module
Transforms raw match data into ML-ready features
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle


class MatchPreprocessor:
    """Preprocess and engineer features for match prediction"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
    def prepare_training_data(self, matches_df: pd.DataFrame, rankings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw matches into ML-ready features
        
        Features include:
        - rank_difference
        - form_score (last 5 matches)
        - goals_avg_last5
        - win_ratio
        - head_to_head_record
        - confederation_matchup
        """
        print("🔧 Preprocessing match data and engineering features...")
        
        # Create a copy
        df = matches_df.copy()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date (important for temporal features)
        df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate match result
        df['result'] = df.apply(lambda row: self._get_result(row), axis=1)
        
        # Merge rankings
        df = self._merge_rankings(df, rankings_df)
        
        # Engineer features
        df = self._engineer_features(df)
        
        # Create target variable
        df['target'] = df['result'].map({'H': 0, 'D': 1, 'A': 2})
        
        # Remove matches with missing critical data
        df = df.dropna(subset=['target', 'rank_home', 'rank_away'])
        
        print(f"✅ Preprocessed {len(df)} matches with {len(df.columns)} features")
        
        return df
    
    def _get_result(self, row) -> str:
        """Determine match result: H (home win), D (draw), A (away win)"""
        if pd.isna(row['goals_home']) or pd.isna(row['goals_away']):
            return None
        
        if row['goals_home'] > row['goals_away']:
            return 'H'
        elif row['goals_home'] < row['goals_away']:
            return 'A'
        else:
            return 'D'
    
    def _merge_rankings(self, df: pd.DataFrame, rankings_df: pd.DataFrame) -> pd.DataFrame:
        """Merge FIFA rankings for home and away teams"""
        # Create ranking lookup
        ranking_map = dict(zip(rankings_df['team'], rankings_df['rank']))
        points_map = dict(zip(rankings_df['team'], rankings_df['points']))
        
        # Map rankings
        df['rank_home'] = df['home_team'].map(ranking_map)
        df['rank_away'] = df['away_team'].map(ranking_map)
        df['points_home'] = df['home_team'].map(points_map)
        df['points_away'] = df['away_team'].map(points_map)
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create predictive features from raw data"""
        
        # 1. Rank difference (negative = home team stronger)
        df['rank_difference'] = df['rank_away'] - df['rank_home']
        df['points_difference'] = df['points_home'] - df['points_away']
        
        # 2. Home advantage (simple binary)
        df['home_advantage'] = 1  # All matches assume some home advantage
        
        # 3. Goal-based features
        if 'goals_home' in df.columns and 'goals_away' in df.columns:
            df['goal_difference'] = df['goals_home'] - df['goals_away']
            df['total_goals'] = df['goals_home'] + df['goals_away']
        
        # 4. Possession-based features (if available)
        if 'possession_home' in df.columns and 'possession_away' in df.columns:
            df['possession_diff'] = df['possession_home'] - df['possession_away']
        else:
            df['possession_diff'] = 0
        
        # 5. Form score (rolling average of last 5 results)
        df = self._calculate_form_scores(df)
        
        # 6. Win ratio (historical)
        df = self._calculate_win_ratios(df)
        
        # 7. Goals average last 5 matches
        df = self._calculate_goals_avg(df)
        
        # 8. Competition importance weight
        df['competition_weight'] = df['competition'].apply(self._get_competition_weight)
        
        return df
    
    def _calculate_form_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate recent form score for each team (last 5 matches)"""
        df['form_home'] = 0.5  # Default neutral form
        df['form_away'] = 0.5
        
        # This would require team-by-team calculation over time
        # Simplified version: use rank as proxy
        df['form_home'] = (100 - df['rank_home']) / 100
        df['form_away'] = (100 - df['rank_away']) / 100
        
        return df
    
    def _calculate_win_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate historical win ratio"""
        # Simplified: use FIFA ranking as proxy
        df['win_ratio_home'] = (100 - df['rank_home']) / 100
        df['win_ratio_away'] = (100 - df['rank_away']) / 100
        
        return df
    
    def _calculate_goals_avg(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate average goals scored in last 5 matches"""
        # Simplified: estimate based on team strength
        df['goals_avg_home'] = 1.5 + (100 - df['rank_home']) / 100
        df['goals_avg_away'] = 1.5 + (100 - df['rank_away']) / 100
        
        return df
    
    def _get_competition_weight(self, competition: str) -> float:
        """Assign weight to match based on competition importance"""
        if pd.isna(competition):
            return 0.5
        
        competition_lower = str(competition).lower()
        
        if 'world cup' in competition_lower and 'qualifier' not in competition_lower:
            return 1.0
        elif 'qualifier' in competition_lower:
            return 0.8
        elif 'friendly' in competition_lower:
            return 0.3
        else:
            return 0.6
    
    def prepare_prediction_features(self, home_team: str, away_team: str, 
                                   rankings_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for a single match prediction"""
        # Get team rankings
        ranking_map = dict(zip(rankings_df['team'], rankings_df['rank']))
        points_map = dict(zip(rankings_df['team'], rankings_df['points']))
        
        home_rank = ranking_map.get(home_team, 50)
        away_rank = ranking_map.get(away_team, 50)
        home_points = points_map.get(home_team, 1500)
        away_points = points_map.get(away_team, 1500)
        
        # Create feature dictionary
        features = {
            'rank_home': home_rank,
            'rank_away': away_rank,
            'points_home': home_points,
            'points_away': away_points,
            'rank_difference': away_rank - home_rank,
            'points_difference': home_points - away_points,
            'home_advantage': 1,
            'possession_diff': 0,
            'form_home': (100 - home_rank) / 100,
            'form_away': (100 - away_rank) / 100,
            'win_ratio_home': (100 - home_rank) / 100,
            'win_ratio_away': (100 - away_rank) / 100,
            'goals_avg_home': 1.5 + (100 - home_rank) / 100,
            'goals_avg_away': 1.5 + (100 - away_rank) / 100,
            'competition_weight': 1.0,  # Assume World Cup importance
        }
        
        return pd.DataFrame([features])
    
    def get_feature_columns(self) -> list:
        """Return list of feature columns used for training"""
        return [
            'rank_home', 'rank_away', 'points_home', 'points_away',
            'rank_difference', 'points_difference', 'home_advantage',
            'possession_diff', 'form_home', 'form_away',
            'win_ratio_home', 'win_ratio_away',
            'goals_avg_home', 'goals_avg_away',
            'competition_weight'
        ]
    
    def split_temporal(self, df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data temporally (train on older, test on newer)"""
        df = df.sort_values('date')
        split_idx = int(len(df) * (1 - test_size))
        
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        print(f"📊 Temporal split: {len(train_df)} train, {len(test_df)} test")
        print(f"   Train period: {train_df['date'].min()} to {train_df['date'].max()}")
        print(f"   Test period: {test_df['date'].min()} to {test_df['date'].max()}")
        
        return train_df, test_df


def load_and_preprocess(matches_df: pd.DataFrame, rankings_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Main preprocessing pipeline"""
    preprocessor = MatchPreprocessor()
    
    # Prepare data
    processed_df = preprocessor.prepare_training_data(matches_df, rankings_df)
    
    # Temporal split
    train_df, test_df = preprocessor.split_temporal(processed_df, test_size=0.2)
    
    return train_df, test_df, preprocessor


if __name__ == "__main__":
    # Test preprocessing
    from data_collection import collect_all_data
    
    data = collect_all_data()
    train_df, test_df, preprocessor = load_and_preprocess(
        data['matches'], 
        data['rankings']
    )
    
    print("\n✅ Preprocessing complete!")
    print(f"   Features: {preprocessor.get_feature_columns()}")
    print(f"\n📊 Sample training data:")
    print(train_df[preprocessor.get_feature_columns()].head())
