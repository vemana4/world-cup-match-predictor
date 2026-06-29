import sys
from unittest.mock import MagicMock, patch

# Mock out heavy ML modules to allow fast local testing without full package builds
sys.modules['xgboost'] = MagicMock()
sys.modules['catboost'] = MagicMock()

# Mock out database components that might trigger sqlite operations
sys.modules['database'] = MagicMock()

from ml.tournament_simulator import TournamentSimulator

@patch('ml.tournament_simulator.PredictionEngine')
def test_tournament_simulator_simulate(mock_prediction_engine_class):
    mock_engine = MagicMock()
    mock_prediction = MagicMock()
    mock_prediction.predicted_home_goals = 2.0
    mock_prediction.predicted_away_goals = 1.0
    mock_engine.predict_match.return_value = mock_prediction
    mock_prediction_engine_class.return_value = mock_engine
    
    simulator = TournamentSimulator()
    
    test_teams = ["Argentina", "France", "Brazil", "England", "Spain", "Portugal", "Germany", "Morocco"]
    result = simulator.simulate(num_simulations=100, teams=test_teams, db=None)
    
    assert 'finalist_probabilities' in result
    assert 'winner_probabilities' in result
    assert len(result['winner_probabilities']) > 0

@patch('ml.tournament_simulator.PredictionEngine')
def test_simulate_match_fallback_on_exception(mock_prediction_engine_class):
    mock_engine = MagicMock()
    mock_engine.predict_match.side_effect = Exception("Prediction Engine Error")
    mock_prediction_engine_class.return_value = mock_engine
    
    simulator = TournamentSimulator()
    winner = simulator._simulate_match("Argentina", "France", db=None)
    
    assert winner in ["Argentina", "France"]
