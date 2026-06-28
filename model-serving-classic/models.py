"""
Database models for FIFA 2026 Prediction System
Uses SQLAlchemy ORM with PostgreSQL
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ENUM
import enum

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class QualificationStatus(enum.Enum):
    """Team qualification status for FIFA 2026"""
    QUALIFIED = "qualified"
    PROVISIONAL = "provisional"
    CANDIDATE = "candidate"


class Team(Base):
    """FIFA Team data with dynamic qualification tracking"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    fifa_code = Column(String(3), unique=True, nullable=False)
    confederation = Column(String, nullable=False)  # UEFA, CONMEBOL, AFC, CAF, CONCACAF, OFC
    current_rank = Column(Integer)
    fifa_points = Column(Float)
    qualification_status = Column(ENUM(QualificationStatus, name='qualificationstatus', create_type=False), default=QualificationStatus.CANDIDATE)
    world_cup_appearances = Column(Integer, default=0)  # Historical WC count (2006-2022)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    home_matches = relationship("Match", back_populates="home_team", foreign_keys="Match.home_team_id")
    away_matches = relationship("Match", back_populates="away_team", foreign_keys="Match.away_team_id")


class Match(Base):
    """Historical and live match data"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, unique=True, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Match statistics
    goals_home = Column(Integer)
    goals_away = Column(Integer)
    possession_home = Column(Float)
    possession_away = Column(Float)
    shots_on_target_home = Column(Integer)
    shots_on_target_away = Column(Integer)
    corners_home = Column(Integer)
    corners_away = Column(Integer)
    fouls_home = Column(Integer)
    fouls_away = Column(Integer)
    yellow_cards_home = Column(Integer)
    yellow_cards_away = Column(Integer)
    red_cards_home = Column(Integer)
    red_cards_away = Column(Integer)
    
    # Match context
    competition = Column(String)  # World Cup, Qualifier, Friendly
    venue = Column(String)
    is_neutral = Column(Integer, default=0)  # 1 if neutral venue
    
    # Rankings at time of match
    home_rank = Column(Integer)
    away_rank = Column(Integer)
    
    # Match outcome (for training)
    result = Column(String)  # 'H' (home win), 'D' (draw), 'A' (away win)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    home_team = relationship("Team", back_populates="home_matches", foreign_keys=[home_team_id])
    away_team = relationship("Team", back_populates="away_matches", foreign_keys=[away_team_id])


class Prediction(Base):
    """Model predictions for upcoming matches"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, nullable=False, index=True)
    prediction_date = Column(DateTime, default=datetime.utcnow)
    
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Predicted probabilities
    prob_home_win = Column(Float)
    prob_draw = Column(Float)
    prob_away_win = Column(Float)
    
    # Model metadata
    model_version = Column(String, default="xgboost_v1")
    confidence_score = Column(Float)
    
    # Anomaly detection
    anomaly_score = Column(Float)  # 0-1, where 1 = normal
    
    created_at = Column(DateTime, default=datetime.utcnow)


class RankingHistory(Base):
    """Historical FIFA ranking snapshots"""
    __tablename__ = "ranking_history"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    rank = Column(Integer, nullable=False)
    points = Column(Float, nullable=False)
    snapshot_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataIngestionLog(Base):
    """Log data collection and scraping events"""
    __tablename__ = "data_ingestion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # 'fifa_scraper', 'api_football', etc.
    status = Column(String, nullable=False)  # 'success', 'error', 'partial'
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    error_message = Column(String)
    execution_time = Column(Float)  # seconds
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


def init_db():
    """Initialize database tables"""
    from sqlalchemy import text
    
    # Create enum type if it doesn't exist
    with engine.connect() as conn:
        # Check if enum type exists
        result = conn.execute(
            text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'qualificationstatus')")
        )
        enum_exists = result.scalar()
        
        if not enum_exists:
            conn.execute(text("CREATE TYPE qualificationstatus AS ENUM ('QUALIFIED', 'PROVISIONAL', 'CANDIDATE')"))
            conn.commit()
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
