from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import Team, Player, PlayerStats_xG, PlayerMarketValue, InjuryReport, Match
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Dynamic, context-aware feature engineering at prediction time.
    Implements Phase 4.3: starting_xi features, market values, xG stats, injury penalties.
    """
    
    def __init__(self):
        logger.info("FeatureEngineer initialized")
    
    def engineer_features(
        self,
        home_team_id: int,
        away_team_id: int,
        db: Session,
        scheduled_date: datetime
    ) -> dict:
        """
        Engineer all features for a match prediction.
        """
        features = {}
        
        home_team = db.query(Team).filter(Team.id == home_team_id).first()
        away_team = db.query(Team).filter(Team.id == away_team_id).first()
        
        features['rank_difference'] = (away_team.fifa_rank or 50) - (home_team.fifa_rank or 50)
        features['points_difference'] = (home_team.fifa_points or 1000) - (away_team.fifa_points or 1000)
        
        features['home_form'] = self._calculate_team_form(home_team_id, db)
        features['away_form'] = self._calculate_team_form(away_team_id, db)
        
        features['home_win_ratio'] = self._calculate_win_ratio(home_team_id, db, is_home=True)
        features['away_win_ratio'] = self._calculate_win_ratio(away_team_id, db, is_home=False)
        
        home_xi_features = self._get_starting_xi_features(home_team_id, db, scheduled_date)
        away_xi_features = self._get_starting_xi_features(away_team_id, db, scheduled_date)
        
        features['starting_xi_market_value'] = home_xi_features['total_market_value'] - away_xi_features['total_market_value']
        features['starting_xi_avg_xg'] = home_xi_features['avg_xg'] - away_xi_features['avg_xg']
        features['starting_xi_avg_defensive_actions'] = home_xi_features['avg_defensive'] - away_xi_features['avg_defensive']
        
        home_injury_penalty = self._calculate_injury_penalty(home_team_id, db, scheduled_date)
        away_injury_penalty = self._calculate_injury_penalty(away_team_id, db, scheduled_date)
        features['key_player_injury_penalty'] = home_injury_penalty - away_injury_penalty
        
        features['team_morale_home'] = 0.0
        features['team_morale_away'] = 0.0
        features['public_pressure_home'] = 0.0
        features['public_pressure_away'] = 0.0
        
        logger.info(f"Engineered {len(features)} features for match prediction")
        return features
    
    def _calculate_team_form(self, team_id: int, db: Session, num_matches: int = 5):
        """
        Calculate team form based on last N matches.
        """
        recent_matches = db.query(Match).filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        ).filter(
            Match.home_goals.isnot(None)
        ).order_by(Match.match_date.desc()).limit(num_matches).all()
        
        if not recent_matches:
            return 0.5
        
        points = 0
        for match in recent_matches:
            if match.home_team_id == team_id:
                if match.home_goals > match.away_goals:
                    points += 3
                elif match.home_goals == match.away_goals:
                    points += 1
            else:
                if match.away_goals > match.home_goals:
                    points += 3
                elif match.away_goals == match.home_goals:
                    points += 1
        
        max_points = num_matches * 3
        return points / max_points if max_points > 0 else 0.5
    
    def _calculate_win_ratio(self, team_id: int, db: Session, is_home: bool = True):
        """
        Calculate historical win ratio for team.
        """
        if is_home:
            matches = db.query(Match).filter(
                Match.home_team_id == team_id,
                Match.home_goals.isnot(None)
            ).all()
        else:
            matches = db.query(Match).filter(
                Match.away_team_id == team_id,
                Match.away_goals.isnot(None)
            ).all()
        
        if not matches:
            return 0.5
        
        wins = 0
        for match in matches:
            if is_home and match.home_goals > match.away_goals:
                wins += 1
            elif not is_home and match.away_goals > match.home_goals:
                wins += 1
        
        return wins / len(matches) if matches else 0.5
    
    def _get_starting_xi_features(self, team_id: int, db: Session, scheduled_date: datetime):
        """
        Get aggregated features for Starting XI players.
        Phase 4.3: Critical accuracy boost from player-level data.
        """
        cutoff_date = scheduled_date - timedelta(days=90)
        
        players = db.query(Player).filter(Player.team_id == team_id).limit(11).all()
        
        total_market_value = 0
        xg_values = []
        defensive_actions = []
        
        for player in players:
            market_value = db.query(PlayerMarketValue).filter(
                PlayerMarketValue.player_id == player.id
            ).order_by(PlayerMarketValue.valuation_date.desc()).first()
            
            if market_value:
                total_market_value += market_value.market_value_eur or 0
            
            recent_stats = db.query(PlayerStats_xG).filter(
                PlayerStats_xG.player_id == player.id,
                PlayerStats_xG.match_date >= cutoff_date
            ).all()
            
            if recent_stats:
                avg_xg = sum(s.xg or 0 for s in recent_stats) / len(recent_stats)
                avg_def = sum(s.defensive_actions or 0 for s in recent_stats) / len(recent_stats)
                xg_values.append(avg_xg)
                defensive_actions.append(avg_def)
        
        return {
            'total_market_value': total_market_value / 1_000_000,
            'avg_xg': sum(xg_values) / len(xg_values) if xg_values else 0.0,
            'avg_defensive': sum(defensive_actions) / len(defensive_actions) if defensive_actions else 0.0
        }
    
    def _calculate_injury_penalty(self, team_id: int, db: Session, scheduled_date: datetime):
        """
        Calculate penalty based on injured/suspended key players.
        Phase 3.1: NLP-detected injuries significantly impact predictions.
        """
        active_injuries = db.query(InjuryReport).join(
            Player, InjuryReport.player_id == Player.id
        ).filter(
            Player.team_id == team_id,
            InjuryReport.is_active == True,
            InjuryReport.report_date <= scheduled_date
        ).all()
        
        if not active_injuries:
            return 0.0
        
        penalty = len(active_injuries) * -5.0
        
        for injury in active_injuries:
            if injury.severity in ['severe', 'major']:
                penalty -= 10.0
        
        return penalty
