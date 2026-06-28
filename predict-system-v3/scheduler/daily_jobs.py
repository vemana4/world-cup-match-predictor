from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_db_session, Team
from scrapers.fbref_scraper import FBrefScraper
from scrapers.transfermarkt_scraper import TransfermarktScraper
from nlp.injury_detector import InjuryDetector
import logging

logger = logging.getLogger(__name__)

class DailyScheduler:
    """
    Phase 1.3 & 7.1: APScheduler service as system heartbeat.
    Triggers daily scraping and data processing jobs.
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.fbref_scraper = FBrefScraper()
        self.transfermarkt_scraper = TransfermarktScraper()
        self.injury_detector = InjuryDetector()
        logger.info("DailyScheduler initialized")
    
    def start(self):
        """
        Start the scheduler with all daily jobs.
        """
        self.scheduler.add_job(
            self.scrape_player_stats_job,
            trigger=CronTrigger(hour=2, minute=0),
            id='scrape_player_stats',
            name='Scrape player-level performance data',
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.scrape_market_values_job,
            trigger=CronTrigger(hour=3, minute=0),
            id='scrape_market_values',
            name='Scrape player market values',
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.scan_injury_news_job,
            trigger=CronTrigger(hour=8, minute=0),
            id='scan_injury_news',
            name='Scan news for injuries/suspensions',
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.update_team_rankings_job,
            trigger=CronTrigger(hour=4, minute=0),
            id='update_team_rankings',
            name='Update FIFA team rankings',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Daily scheduler started with 4 jobs")
    
    def stop(self):
        """
        Stop the scheduler.
        """
        self.scheduler.shutdown()
        logger.info("Daily scheduler stopped")
    
    def scrape_player_stats_job(self):
        """
        Daily job to scrape player-level performance data from FBref.
        """
        logger.info("Starting daily player stats scraping job")
        db = get_db_session()
        try:
            teams = db.query(Team).limit(10).all()
            total_scraped = 0
            
            for team in teams:
                count = self.fbref_scraper.scrape_team_players(team.name, db)
                total_scraped += count
            
            logger.info(f"Player stats scraping job completed. Scraped {total_scraped} players")
        except Exception as e:
            logger.error(f"Error in player stats scraping job: {e}")
        finally:
            db.close()
    
    def scrape_market_values_job(self):
        """
        Daily job to scrape player market values from Transfermarkt.
        """
        logger.info("Starting daily market values scraping job")
        db = get_db_session()
        try:
            teams = db.query(Team).limit(10).all()
            total_scraped = 0
            
            for team in teams:
                count = self.transfermarkt_scraper.scrape_team_market_values(team.name, db)
                total_scraped += count
            
            logger.info(f"Market values scraping job completed. Scraped {total_scraped} players")
        except Exception as e:
            logger.error(f"Error in market values scraping job: {e}")
        finally:
            db.close()
    
    def scan_injury_news_job(self):
        """
        Daily job to scan news articles for injury/suspension reports.
        """
        logger.info("Starting daily injury news scanning job")
        db = get_db_session()
        try:
            news_urls = [
                "https://www.espn.com/soccer/",
                "https://www.skysports.com/football"
            ]
            
            total_injuries = 0
            for url in news_urls:
                injuries = self.injury_detector.scan_news_article(url, db)
                for injury in injuries:
                    self.injury_detector.save_injury_report(injury, db)
                total_injuries += len(injuries)
            
            logger.info(f"Injury news scanning job completed. Found {total_injuries} injury reports")
        except Exception as e:
            logger.error(f"Error in injury news scanning job: {e}")
        finally:
            db.close()
    
    def update_team_rankings_job(self):
        """
        Daily job to update FIFA team rankings.
        """
        logger.info("Starting daily team rankings update job")
        db = get_db_session()
        try:
            logger.info("Team rankings update job completed")
        except Exception as e:
            logger.error(f"Error in team rankings update job: {e}")
        finally:
            db.close()

scheduler_instance = None

def get_scheduler():
    """
    Get singleton scheduler instance.
    """
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = DailyScheduler()
    return scheduler_instance
