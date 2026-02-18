"""
Celery Beat Schedule Configuration

ASSUMPTIONS:
- Beat is running
- UPSC/SSC need frequent updates (every 2 hours)
"""

from celery.schedules import crontab

beat_schedule = {
    "run_upsc_scraper": {
        "task": "src.scrapers.scheduler.tasks.run_upsc_scraper",
        "schedule": crontab(minute=0, hour="*/2"),
    },
    "run_ssc_scraper": {
        "task": "src.scrapers.scheduler.tasks.run_ssc_scraper",
        "schedule": crontab(minute=30, hour="*/2"),
    },
    "run_auto_update": {
        "task": "src.scrapers.scheduler.auto_update_task.run_auto_update",
        "schedule": crontab(minute=15, hour="*/2"),
    },
}
