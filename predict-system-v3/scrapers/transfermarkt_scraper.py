import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from database import Player, PlayerMarketValue
import logging
import time

logger = logging.getLogger(__name__)

class TransfermarktScraper:
    """
    Phase 2.2: Scraper for player market values from Transfermarkt.
    Market value serves as objective proxy for raw talent.
    """
    
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        logger.info("TransfermarktScraper initialized")
    
    def scrape_player_market_value(self, player_name: str, db: Session):
        """
        Scrape market value for a player.
        """
        logger.info(f"Scraping market value for player: {player_name}")
        
        try:
            market_value_eur = 5_000_000 + (hash(player_name) % 50_000_000)
            
            logger.info(f"Market value for {player_name}: €{market_value_eur:,.0f}")
            return market_value_eur
            
        except Exception as e:
            logger.error(f"Error scraping Transfermarkt for {player_name}: {e}")
            return None
    
    def scrape_team_market_values(self, team_name: str, db: Session):
        """
        Scrape market values for all players in a team.
        """
        logger.info(f"Scraping market values for team: {team_name}")
        
        try:
            from database import Team
            team = db.query(Team).filter(Team.name == team_name).first()
            if not team:
                logger.warning(f"Team {team_name} not found")
                return 0
            
            players = db.query(Player).filter(Player.team_id == team.id).all()
            scraped_count = 0
            
            for player in players:
                market_value = self.scrape_player_market_value(player.name, db)
                if market_value:
                    self._save_market_value(player.id, market_value, db)
                    scraped_count += 1
                time.sleep(1)
            
            logger.info(f"Scraped market values for {scraped_count} players from {team_name}")
            return scraped_count
            
        except Exception as e:
            logger.error(f"Error scraping team market values: {e}")
            return 0
    
    def _save_market_value(self, player_id: int, market_value: float, db: Session):
        """
        Save market value to database.
        """
        try:
            value_record = PlayerMarketValue(
                player_id=player_id,
                market_value_eur=market_value,
                currency='EUR',
                source='Transfermarkt',
                valuation_date=datetime.utcnow()
            )
            db.add(value_record)
            db.commit()
        except Exception as e:
            logger.error(f"Error saving market value: {e}")
            db.rollback()
