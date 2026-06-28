import sys
sys.path.append('.')

from database import init_db, get_db_session, Team, Player
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """
    Initialize database with schema and sample FIFA teams.
    """
    logger.info("Initializing database...")
    
    init_db()
    
    db = get_db_session()
    
    try:
        existing_teams = db.query(Team).count()
        if existing_teams > 0:
            logger.info(f"Database already has {existing_teams} teams. Skipping initialization.")
            return
        
        logger.info("Adding FIFA 2026 World Cup qualified teams...")
        
        teams_data = [
            {"name": "Brazil", "country_code": "BRA", "fifa_rank": 1, "fifa_points": 1840.77, "confederation": "CONMEBOL"},
            {"name": "Argentina", "country_code": "ARG", "fifa_rank": 2, "fifa_points": 1838.38, "confederation": "CONMEBOL"},
            {"name": "France", "country_code": "FRA", "fifa_rank": 3, "fifa_points": 1823.39, "confederation": "UEFA"},
            {"name": "Belgium", "country_code": "BEL", "fifa_rank": 4, "fifa_points": 1781.30, "confederation": "UEFA"},
            {"name": "England", "country_code": "ENG", "fifa_rank": 5, "fifa_points": 1774.19, "confederation": "UEFA"},
            {"name": "Netherlands", "country_code": "NED", "fifa_rank": 6, "fifa_points": 1758.51, "confederation": "UEFA"},
            {"name": "Croatia", "country_code": "CRO", "fifa_rank": 7, "fifa_points": 1742.55, "confederation": "UEFA"},
            {"name": "Italy", "country_code": "ITA", "fifa_rank": 8, "fifa_points": 1731.51, "confederation": "UEFA"},
            {"name": "Portugal", "country_code": "POR", "fifa_rank": 9, "fifa_points": 1727.42, "confederation": "UEFA"},
            {"name": "Spain", "country_code": "ESP", "fifa_rank": 10, "fifa_points": 1716.93, "confederation": "UEFA"},
            {"name": "Morocco", "country_code": "MAR", "fifa_rank": 11, "fifa_points": 1676.24, "confederation": "CAF"},
            {"name": "USA", "country_code": "USA", "fifa_rank": 13, "fifa_points": 1668.33, "confederation": "CONCACAF"},
            {"name": "Mexico", "country_code": "MEX", "fifa_rank": 15, "fifa_points": 1653.73, "confederation": "CONCACAF"},
            {"name": "Japan", "country_code": "JPN", "fifa_rank": 18, "fifa_points": 1628.99, "confederation": "AFC"},
            {"name": "Senegal", "country_code": "SEN", "fifa_rank": 19, "fifa_points": 1619.65, "confederation": "CAF"},
            {"name": "Germany", "country_code": "GER", "fifa_rank": 12, "fifa_points": 1666.11, "confederation": "UEFA"},
            {"name": "Uruguay", "country_code": "URU", "fifa_rank": 14, "fifa_points": 1665.49, "confederation": "CONMEBOL"},
            {"name": "Colombia", "country_code": "COL", "fifa_rank": 16, "fifa_points": 1650.70, "confederation": "CONMEBOL"},
            {"name": "Denmark", "country_code": "DEN", "fifa_rank": 17, "fifa_points": 1634.94, "confederation": "UEFA"},
            {"name": "South Korea", "country_code": "KOR", "fifa_rank": 20, "fifa_points": 1617.81, "confederation": "AFC"},
            {"name": "Australia", "country_code": "AUS", "fifa_rank": 25, "fifa_points": 1584.58, "confederation": "AFC"},
            {"name": "Canada", "country_code": "CAN", "fifa_rank": 40, "fifa_points": 1505.68, "confederation": "CONCACAF"},
            {"name": "Ecuador", "country_code": "ECU", "fifa_rank": 28, "fifa_points": 1563.57, "confederation": "CONMEBOL"},
            {"name": "Iran", "country_code": "IRN", "fifa_rank": 21, "fifa_points": 1604.62, "confederation": "AFC"},
            {"name": "Egypt", "country_code": "EGY", "fifa_rank": 36, "fifa_points": 1513.35, "confederation": "CAF"},
            {"name": "Ghana", "country_code": "GHA", "fifa_rank": 60, "fifa_points": 1393.47, "confederation": "CAF"},
            {"name": "Tunisia", "country_code": "TUN", "fifa_rank": 30, "fifa_points": 1551.26, "confederation": "CAF"},
            {"name": "Nigeria", "country_code": "NGA", "fifa_rank": 38, "fifa_points": 1508.08, "confederation": "CAF"},
            {"name": "Cameroon", "country_code": "CMR", "fifa_rank": 51, "fifa_points": 1429.22, "confederation": "CAF"},
            {"name": "Serbia", "country_code": "SRB", "fifa_rank": 29, "fifa_points": 1560.92, "confederation": "UEFA"},
            {"name": "Poland", "country_code": "POL", "fifa_rank": 31, "fifa_points": 1548.59, "confederation": "UEFA"},
            {"name": "Switzerland", "country_code": "SUI", "fifa_rank": 14, "fifa_points": 1665.26, "confederation": "UEFA"},
        ]
        
        for team_data in teams_data:
            team = Team(**team_data)
            db.add(team)
        
        db.commit()
        logger.info(f"Added {len(teams_data)} teams to database")
        
        logger.info("Adding sample players for top teams...")
        
        brazil_team = db.query(Team).filter(Team.name == "Brazil").first()
        france_team = db.query(Team).filter(Team.name == "France").first()
        
        if brazil_team:
            brazil_players = [
                {"name": "Neymar Jr", "team_id": brazil_team.id, "position": "Forward", "age": 31, "nationality": "Brazil"},
                {"name": "Vinicius Junior", "team_id": brazil_team.id, "position": "Forward", "age": 23, "nationality": "Brazil"},
                {"name": "Casemiro", "team_id": brazil_team.id, "position": "Midfielder", "age": 31, "nationality": "Brazil"},
                {"name": "Alisson", "team_id": brazil_team.id, "position": "Goalkeeper", "age": 31, "nationality": "Brazil"},
                {"name": "Marquinhos", "team_id": brazil_team.id, "position": "Defender", "age": 29, "nationality": "Brazil"},
                {"name": "Richarlison", "team_id": brazil_team.id, "position": "Forward", "age": 26, "nationality": "Brazil"},
                {"name": "Bruno Guimaraes", "team_id": brazil_team.id, "position": "Midfielder", "age": 25, "nationality": "Brazil"},
                {"name": "Eder Militao", "team_id": brazil_team.id, "position": "Defender", "age": 25, "nationality": "Brazil"},
                {"name": "Raphinha", "team_id": brazil_team.id, "position": "Forward", "age": 27, "nationality": "Brazil"},
                {"name": "Lucas Paqueta", "team_id": brazil_team.id, "position": "Midfielder", "age": 26, "nationality": "Brazil"},
                {"name": "Danilo", "team_id": brazil_team.id, "position": "Defender", "age": 32, "nationality": "Brazil"},
            ]
            
            for player_data in brazil_players:
                player = Player(**player_data)
                db.add(player)
        
        if france_team:
            france_players = [
                {"name": "Kylian Mbappe", "team_id": france_team.id, "position": "Forward", "age": 25, "nationality": "France"},
                {"name": "Antoine Griezmann", "team_id": france_team.id, "position": "Forward", "age": 33, "nationality": "France"},
                {"name": "N'Golo Kante", "team_id": france_team.id, "position": "Midfielder", "age": 32, "nationality": "France"},
                {"name": "Hugo Lloris", "team_id": france_team.id, "position": "Goalkeeper", "age": 37, "nationality": "France"},
                {"name": "Raphael Varane", "team_id": france_team.id, "position": "Defender", "age": 30, "nationality": "France"},
                {"name": "Aurelien Tchouameni", "team_id": france_team.id, "position": "Midfielder", "age": 24, "nationality": "France"},
                {"name": "Dayot Upamecano", "team_id": france_team.id, "position": "Defender", "age": 25, "nationality": "France"},
                {"name": "Jules Kounde", "team_id": france_team.id, "position": "Defender", "age": 25, "nationality": "France"},
                {"name": "Ousmane Dembele", "team_id": france_team.id, "position": "Forward", "age": 26, "nationality": "France"},
                {"name": "Eduardo Camavinga", "team_id": france_team.id, "position": "Midfielder", "age": 21, "nationality": "France"},
                {"name": "Theo Hernandez", "team_id": france_team.id, "position": "Defender", "age": 26, "nationality": "France"},
            ]
            
            for player_data in france_players:
                player = Player(**player_data)
                db.add(player)
        
        db.commit()
        logger.info("Added sample players to database")
        
        logger.info("✅ Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
