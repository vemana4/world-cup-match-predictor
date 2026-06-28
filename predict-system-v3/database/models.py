from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    country_code = Column(String(3), nullable=False)
    fifa_rank = Column(Integer)
    fifa_points = Column(Float)
    confederation = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    players = relationship("Player", back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    fixtures_home = relationship("LiveFixture", foreign_keys="LiveFixture.home_team_id", back_populates="home_team")
    fixtures_away = relationship("LiveFixture", foreign_keys="LiveFixture.away_team_id", back_populates="away_team")

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))
    position = Column(String(50))
    age = Column(Integer)
    nationality = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    team = relationship("Team", back_populates="players")
    stats = relationship("PlayerStats_xG", back_populates="player")
    market_values = relationship("PlayerMarketValue", back_populates="player")
    injury_reports = relationship("InjuryReport", back_populates="player")

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    match_date = Column(DateTime, nullable=False)
    competition = Column(String(100))
    competition_importance = Column(Float, default=1.0)
    venue = Column(String(200))
    attendance = Column(Integer)
    referee_id = Column(Integer, ForeignKey('referee_stats.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    referee = relationship("RefereeStats", back_populates="matches")
    predictions = relationship("ModelPrediction", back_populates="match")

class LiveFixture(Base):
    __tablename__ = 'live_fixtures'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    competition = Column(String(100))
    venue = Column(String(200))
    stadium_location = Column(String(200))
    referee_id = Column(Integer, ForeignKey('referee_stats.id'))
    status = Column(String(50), default='scheduled')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="fixtures_home")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="fixtures_away")
    referee = relationship("RefereeStats", back_populates="fixtures")
    predictions = relationship("ModelPrediction", back_populates="fixture")
    betting_odds = relationship("BettingOdds_Live", back_populates="fixture")

class PlayerStats_xG(Base):
    __tablename__ = 'player_stats_xg'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    season = Column(String(20))
    match_date = Column(DateTime)
    xg = Column(Float, default=0.0)
    xa = Column(Float, default=0.0)
    pressures = Column(Integer, default=0)
    tackles_successful = Column(Integer, default=0)
    defensive_actions = Column(Integer, default=0)
    rating = Column(Float)
    minutes_played = Column(Integer, default=0)
    rolling_5game_xg = Column(Float)
    rolling_5game_xa = Column(Float)
    rolling_5game_rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="stats")

class PlayerMarketValue(Base):
    __tablename__ = 'player_market_values'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    market_value_eur = Column(Float)
    currency = Column(String(10), default='EUR')
    source = Column(String(50), default='Transfermarkt')
    valuation_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="market_values")

class RefereeStats(Base):
    __tablename__ = 'referee_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    nationality = Column(String(50))
    avg_cards_per_match = Column(Float, default=0.0)
    avg_yellow_cards = Column(Float, default=0.0)
    avg_red_cards = Column(Float, default=0.0)
    home_win_bias_pct = Column(Float, default=0.0)
    total_matches_officiated = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    matches = relationship("Match", back_populates="referee")
    fixtures = relationship("LiveFixture", back_populates="referee")

class InjuryReport(Base):
    __tablename__ = 'injury_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    status = Column(String(50), nullable=False)
    severity = Column(String(50))
    injury_type = Column(String(100))
    detection_source = Column(String(200))
    report_date = Column(DateTime, nullable=False)
    expected_return_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="injury_reports")

class BettingOdds_Live(Base):
    __tablename__ = 'betting_odds_live'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey('live_fixtures.id'), nullable=False)
    bookmaker = Column(String(100))
    home_win_opening = Column(Float)
    draw_opening = Column(Float)
    away_win_opening = Column(Float)
    home_win_closing = Column(Float)
    draw_closing = Column(Float)
    away_win_closing = Column(Float)
    betting_volume_home = Column(Float)
    betting_volume_draw = Column(Float)
    betting_volume_away = Column(Float)
    line_movement_velocity = Column(Float)
    timestamp_opening = Column(DateTime)
    timestamp_closing = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    fixture = relationship("LiveFixture", back_populates="betting_odds")

class ModelPrediction(Base):
    __tablename__ = 'model_predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=True)
    fixture_id = Column(Integer, ForeignKey('live_fixtures.id'), nullable=True)
    model_version = Column(String(50), nullable=False)
    prediction_type = Column(String(50), nullable=False)
    predicted_home_goals = Column(Float)
    predicted_away_goals = Column(Float)
    home_win_prob = Column(Float)
    draw_prob = Column(Float)
    away_win_prob = Column(Float)
    most_likely_score = Column(String(20))
    confidence_score = Column(Float)
    anomaly_score = Column(Float)
    is_anomaly = Column(Boolean, default=False)
    prediction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    match = relationship("Match", back_populates="predictions")
    fixture = relationship("LiveFixture", back_populates="predictions")
    explainability = relationship("PredictionExplainability", back_populates="prediction", uselist=False)

class PredictionExplainability(Base):
    __tablename__ = 'prediction_explainability'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey('model_predictions.id'), nullable=False, unique=True)
    feature_importance = Column(JSON)
    shap_values = Column(JSON)
    top_features_explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prediction = relationship("ModelPrediction", back_populates="explainability")


class WeatherData(Base):
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey('live_fixtures.id'), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    precipitation = Column(Float)
    conditions = Column(String(100))
    forecast_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TravelData(Base):
    __tablename__ = 'travel_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey('live_fixtures.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    distance_travelled_km = Column(Float)
    timezones_crossed = Column(Integer)
    travel_time_hours = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
