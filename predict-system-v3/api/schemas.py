from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    country_code: str
    fifa_rank: Optional[int] = None
    fifa_points: Optional[float] = None
    confederation: Optional[str] = None

class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MatchPredictionRequest(BaseModel):
    home_team_name: str
    away_team_name: str
    scheduled_date: Optional[datetime] = None
    competition: Optional[str] = "Friendly"
    venue: Optional[str] = None

class GoalDistribution(BaseModel):
    home_goals: float
    away_goals: float
    score_probabilities: Dict[str, float]

class PredictionResponse(BaseModel):
    match_id: Optional[int] = None
    fixture_id: Optional[int] = None
    home_team: str
    away_team: str
    predicted_home_goals: float
    predicted_away_goals: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    most_likely_score: str
    confidence_score: float
    anomaly_score: Optional[float] = None
    is_anomaly: bool = False
    prediction_date: datetime
    model_version: str

class ExplainabilityResponse(BaseModel):
    prediction_id: int
    top_features: List[Dict[str, float]]
    explanation_text: str
    feature_importance: Dict[str, float]

class LiveFixtureResponse(BaseModel):
    id: int
    home_team: str
    away_team: str
    scheduled_date: datetime
    competition: str
    venue: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True

class TournamentSimulationRequest(BaseModel):
    num_simulations: int = Field(default=10000, ge=1000, le=100000)
    teams: Optional[List[str]] = None
    tournament_format: str = "FIFA_2026"

class TournamentSimulationResponse(BaseModel):
    num_simulations: int
    finalist_probabilities: Dict[str, float]
    winner_probabilities: Dict[str, float]
    simulation_time_seconds: float
    
class InjuryAlertResponse(BaseModel):
    player_name: str
    team_name: str
    status: str
    severity: Optional[str] = None
    detection_source: str
    report_date: datetime
    confidence_score: Optional[float] = None

class WeatherDataResponse(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    conditions: Optional[str] = None

class RefereeStatsResponse(BaseModel):
    name: str
    avg_cards_per_match: float
    home_win_bias_pct: float
    total_matches_officiated: int

class MatchContextResponse(BaseModel):
    weather: Optional[WeatherDataResponse] = None
    referee: Optional[RefereeStatsResponse] = None
    home_travel_distance_km: Optional[float] = None
    away_travel_distance_km: Optional[float] = None
    home_timezones_crossed: Optional[int] = None
    away_timezones_crossed: Optional[int] = None

class BettingOddsResponse(BaseModel):
    bookmaker: str
    home_win_opening: Optional[float] = None
    draw_opening: Optional[float] = None
    away_win_opening: Optional[float] = None
    home_win_closing: Optional[float] = None
    draw_closing: Optional[float] = None
    away_win_closing: Optional[float] = None
    line_movement_velocity: Optional[float] = None
