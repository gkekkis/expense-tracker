import logging
import os
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from ..db.session import SessionLocal
from ..services.expense_service import process_recurring_templates

# Setup path and load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Set up logging to check when the "alarm" goes off
logger = logging.getLogger(__name__)

# Set up scheduler time


# 1. Initialize the scheduler
scheduler = BackgroundScheduler()
SCHEDULER_HOUR = os.getenv("SCHEDULER_HOUR", 0)
SCHEDULER_MINUTE = os.getenv("SCHEDULER_MINUTE", 0)


def scheduled_task():
    logger.info("Starting scheduled recurring transaction check...")
    db = SessionLocal()
    try:
        process_recurring_templates(db)
        db.commit()
        logger.info("Successfully processed recurring transactions.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during scheduled task: {e}")
    finally:
        db.close()


def start_scheduler():
    """Starts the scheduler and adds the jobs."""
    # Run every day at midnight
    scheduler.add_job(
        scheduled_task,
        trigger=CronTrigger(hour=SCHEDULER_HOUR, minute=SCHEDULER_MINUTE),
        id="recurring_expenses_job",
        replace_existing=True,
    )

    # Run once on startup just to catch anything missed
    scheduler.add_job(scheduled_task, id="startup_check")

    scheduler.start()
    logger.info("Scheduler started. Jobs: recurring_expenses_job (Midnight Daily)")


def stop_scheduler():
    """Cleanly shut down the scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler shut down.")
