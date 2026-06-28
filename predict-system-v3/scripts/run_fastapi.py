import sys
sys.path.append('.')

import uvicorn
from api.main import app
from scheduler.daily_jobs import get_scheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Run FastAPI backend server with scheduler.
    """
    logger.info("Starting FastAPI backend server...")
    
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Daily scheduler started")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.stop()
    except Exception as e:
        logger.error(f"Error running server: {e}")
        scheduler.stop()
        raise

if __name__ == "__main__":
    main()
