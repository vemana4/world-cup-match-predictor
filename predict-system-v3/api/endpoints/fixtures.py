from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, LiveFixture, Team
from api import schemas
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/get_live_fixtures", response_model=List[schemas.LiveFixtureResponse])
async def get_live_fixtures(
    limit: int = 50,
    status: str = "scheduled",
    db: Session = Depends(get_db)
):
    """
    Get upcoming live fixtures with optional status filter.
    """
    try:
        query = db.query(LiveFixture).join(
            Team, LiveFixture.home_team_id == Team.id
        )
        
        if status:
            query = query.filter(LiveFixture.status == status)
        
        fixtures = query.order_by(LiveFixture.scheduled_date).limit(limit).all()
        
        result = []
        for fixture in fixtures:
            result.append(schemas.LiveFixtureResponse(
                id=fixture.id,
                home_team=fixture.home_team.name,
                away_team=fixture.away_team.name,
                scheduled_date=fixture.scheduled_date,
                competition=fixture.competition,
                venue=fixture.venue,
                status=fixture.status
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving fixtures: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving fixtures")

@router.get("/fixture/{fixture_id}/context", response_model=schemas.MatchContextResponse)
async def get_fixture_context(
    fixture_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete match context including weather, referee stats, and travel data.
    """
    try:
        from database import WeatherData, RefereeStats, TravelData
        
        fixture = db.query(LiveFixture).filter(LiveFixture.id == fixture_id).first()
        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")
        
        weather = db.query(WeatherData).filter(WeatherData.fixture_id == fixture_id).first()
        referee = None
        if fixture.referee_id:
            referee = db.query(RefereeStats).filter(RefereeStats.id == fixture.referee_id).first()
        
        travel_home = db.query(TravelData).filter(
            TravelData.fixture_id == fixture_id,
            TravelData.team_id == fixture.home_team_id
        ).first()
        
        travel_away = db.query(TravelData).filter(
            TravelData.fixture_id == fixture_id,
            TravelData.team_id == fixture.away_team_id
        ).first()
        
        weather_data = None
        if weather:
            weather_data = schemas.WeatherDataResponse(
                temperature=weather.temperature,
                humidity=weather.humidity,
                wind_speed=weather.wind_speed,
                conditions=weather.conditions
            )
        
        referee_data = None
        if referee:
            referee_data = schemas.RefereeStatsResponse(
                name=referee.name,
                avg_cards_per_match=referee.avg_cards_per_match,
                home_win_bias_pct=referee.home_win_bias_pct,
                total_matches_officiated=referee.total_matches_officiated
            )
        
        return schemas.MatchContextResponse(
            weather=weather_data,
            referee=referee_data,
            home_travel_distance_km=travel_home.distance_travelled_km if travel_home else None,
            away_travel_distance_km=travel_away.distance_travelled_km if travel_away else None,
            home_timezones_crossed=travel_home.timezones_crossed if travel_home else None,
            away_timezones_crossed=travel_away.timezones_crossed if travel_away else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving match context: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving match context")
