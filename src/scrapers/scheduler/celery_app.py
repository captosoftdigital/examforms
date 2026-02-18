"""
Celery App Configuration

ASSUMPTIONS:
- Redis is available at REDIS_URL
- Celery workers are started with correct settings

CONDITIONS:
- Tasks must run without overlapping
- Failures must not crash worker
"""

import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "examforms_scrapers",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["src.scrapers.scheduler"])
