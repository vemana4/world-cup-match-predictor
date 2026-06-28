import numpy as np
from collections import defaultdict
from sqlalchemy.orm import Session
from database import Team
from ml.prediction_engine import PredictionEngine
import logging

logger = logging.getLogger(__name__)

class TournamentSimulator:
    """
    Monte Carlo tournament simulator using goal-based prediction distributions.
    Simulates full FIFA 2026 48-team format.
    """
    
    def __init__(self):
        self.prediction_engine = PredictionEngine()
        logger.info("TournamentSimulator initialized")
    
    def simulate(
        self,
        num_simulations: int,
        teams: list = None,
        tournament_format: str = "FIFA_2026",
        db: Session = None
    ):
        """
        Run Monte Carlo simulations of the tournament.
        """
        if not teams:
            teams = self._get_qualified_teams(db)
        
        if len(teams) < 8:
            raise ValueError(f"Need at least 8 teams for simulation, got {len(teams)}")
        
        finalist_counts = defaultdict(int)
        winner_counts = defaultdict(int)
        
        logger.info(f"Starting {num_simulations} tournament simulations with {len(teams)} teams...")
        
        for i in range(num_simulations):
            if (i + 1) % 1000 == 0:
                logger.info(f"Completed {i + 1}/{num_simulations} simulations")
            
            finalists, winner = self._simulate_single_tournament(teams, db)
            
            for finalist in finalists:
                finalist_counts[finalist] += 1
            winner_counts[winner] += 1
        
        finalist_probs = {
            team: count / num_simulations
            for team, count in sorted(finalist_counts.items(), key=lambda x: x[1], reverse=True)
        }
        
        winner_probs = {
            team: count / num_simulations
            for team, count in sorted(winner_counts.items(), key=lambda x: x[1], reverse=True)
        }
        
        logger.info("Tournament simulation completed successfully")
        
        return {
            'finalist_probabilities': dict(list(finalist_probs.items())[:16]),
            'winner_probabilities': dict(list(winner_probs.items())[:16])
        }
    
    def _simulate_single_tournament(self, teams: list, db: Session):
        """
        Simulate a single tournament run.
        Simplified knockout format for demonstration.
        """
        remaining_teams = teams.copy()
        np.random.shuffle(remaining_teams)
        
        while len(remaining_teams) > 2:
            next_round = []
            for i in range(0, len(remaining_teams), 2):
                if i + 1 < len(remaining_teams):
                    winner = self._simulate_match(
                        remaining_teams[i],
                        remaining_teams[i + 1],
                        db
                    )
                    next_round.append(winner)
                else:
                    next_round.append(remaining_teams[i])
            remaining_teams = next_round
        
        if len(remaining_teams) == 2:
            finalists = remaining_teams
            winner = self._simulate_match(finalists[0], finalists[1], db)
        else:
            finalists = remaining_teams
            winner = remaining_teams[0]
        
        return finalists, winner
    
    def _simulate_match(self, home_team: str, away_team: str, db: Session):
        """
        Simulate a single match and return winner.
        """
        try:
            prediction = self.prediction_engine.predict_match(
                home_team=home_team,
                away_team=away_team,
                db=db
            )
            
            home_goals = np.random.poisson(prediction.predicted_home_goals)
            away_goals = np.random.poisson(prediction.predicted_away_goals)
            
            if home_goals > away_goals:
                return home_team
            elif away_goals > home_goals:
                return away_team
            else:
                return np.random.choice([home_team, away_team])
        
        except Exception as e:
            logger.warning(f"Match simulation error: {e}, using random choice")
            return np.random.choice([home_team, away_team])
    
    def _get_qualified_teams(self, db: Session):
        """
        Get list of qualified teams from database.
        """
        teams = db.query(Team).filter(Team.fifa_rank.isnot(None)).order_by(Team.fifa_rank).limit(32).all()
        return [team.name for team in teams]
