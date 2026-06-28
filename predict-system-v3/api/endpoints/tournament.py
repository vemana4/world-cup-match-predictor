from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from api import schemas
from ml.tournament_simulator import TournamentSimulator
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

tournament_simulator = None

def get_tournament_simulator():
    global tournament_simulator
    if tournament_simulator is None:
        tournament_simulator = TournamentSimulator()
    return tournament_simulator

@router.post("/simulate_tournament", response_model=schemas.TournamentSimulationResponse)
async def simulate_tournament(
    request: schemas.TournamentSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Run Monte Carlo tournament simulation using goal-based prediction distributions.
    Simulates the full FIFA 2026 48-team format multiple times to estimate probabilities.
    """
    try:
        start_time = time.time()
        simulator = get_tournament_simulator()
        
        results = simulator.simulate(
            num_simulations=request.num_simulations,
            teams=request.teams,
            tournament_format=request.tournament_format,
            db=db
        )
        
        elapsed_time = time.time() - start_time
        
        return schemas.TournamentSimulationResponse(
            num_simulations=request.num_simulations,
            finalist_probabilities=results['finalist_probabilities'],
            winner_probabilities=results['winner_probabilities'],
            simulation_time_seconds=round(elapsed_time, 2)
        )
    except ValueError as e:
        logger.error(f"Tournament simulation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during tournament simulation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during simulation")
