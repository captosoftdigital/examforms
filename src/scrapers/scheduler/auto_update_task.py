"""
Celery Task: Auto-Update System Runner

ASSUMPTIONS:
- auto_update_runner is functional
- Redis/Celery available
"""

from celery import shared_task
from src.auto_update.auto_update_runner import run_auto_update_checks


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def run_auto_update(self):
    try:
        run_auto_update_checks()
        return {"status": "success", "task": "auto_update"}
    except Exception as e:
        raise self.retry(exc=e)
