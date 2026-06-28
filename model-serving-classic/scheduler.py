"""
Automated Data Refresh Scheduler
Runs daily to update FIFA rankings, match data, and retrain models
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging

from data_collection import collect_all_data
from preprocessing import load_and_preprocess
from model_trainer import FIFAMatchPredictor
from models import init_db, SessionLocal, Team, QualificationStatus, DataIngestionLog

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def refresh_data_job():
    """Daily job to refresh all data"""
    logger.info("🚀 Starting daily data refresh...")
    start_time = datetime.now()
    
    try:
        # Collect fresh data
        data = collect_all_data()
        
        # Update database with new rankings
        db = SessionLocal()
        try:
            # Log data ingestion
            log_entry = DataIngestionLog(
                source='daily_refresh',
                status='success',
                records_added=len(data['rankings']),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            db.add(log_entry)
            db.commit()
            
            logger.info(f"✅ Data refresh completed successfully")
            logger.info(f"   - Rankings: {len(data['rankings'])} teams")
            logger.info(f"   - Matches: {len(data['matches'])} historical matches")
            logger.info(f"   - Qualified: {len(data['qualified_teams'])} teams")
            
        except Exception as e:
            logger.error(f"❌ Database update failed: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
        # Optional: Retrain model if significant data changes detected
        # This can be uncommented for production
        # retrain_model_if_needed(data)
        
    except Exception as e:
        logger.error(f"❌ Data refresh job failed: {str(e)}")
        
        # Log failure
        db = SessionLocal()
        try:
            log_entry = DataIngestionLog(
                source='daily_refresh',
                status='error',
                error_message=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()


def retrain_model_if_needed(data):
    """Retrain model if data drift detected"""
    logger.info("🔍 Checking if model retraining is needed...")
    
    # Simplified: retrain weekly or when new data exceeds threshold
    # In production, implement proper drift detection
    
    try:
        # Preprocess data
        from preprocessing import load_and_preprocess
        
        train_df, test_df, preprocessor = load_and_preprocess(
            data['matches'], 
            data['rankings']
        )
        
        # Retrain model
        predictor = FIFAMatchPredictor()
        metrics = predictor.train(train_df, preprocessor.get_feature_columns())
        
        logger.info(f"✅ Model retrained successfully")
        logger.info(f"   Validation Accuracy: {metrics['val_accuracy']*100:.2f}%")
        
    except Exception as e:
        logger.error(f"❌ Model retraining failed: {str(e)}")


def run_scheduler():
    """Run the scheduler"""
    scheduler = BlockingScheduler()
    
    # Schedule daily refresh at 2 AM
    scheduler.add_job(refresh_data_job, 'cron', hour=2, minute=0)
    
    logger.info("⏰ Scheduler started - Daily refresh at 2:00 AM")
    logger.info("Press Ctrl+C to stop")
    
    # Run immediately on startup (optional)
    refresh_data_job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run scheduler
    run_scheduler()
