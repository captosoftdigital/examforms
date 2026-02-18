"""
Scheduled scraper tasks

ASSUMPTIONS:
- Scrapy spiders can run in a Celery task safely
- Tasks should not overlap for same spider
- Runtime limit enforced

FAILURE HANDLING:
- Exceptions caught and logged
- Task returns failure state without killing worker
"""

import logging
from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.scrapers.upsc_scraper_complete import UPSCScraper
from src.scrapers.ssc_scraper_complete import SSCScraper

logger = logging.getLogger(__name__)


def run_spider(spider_cls):
    """
    Run a Scrapy spider safely.
    
    CONDITIONS:
    - Must not raise unhandled exceptions
    - Must finish within task timeout
    """
    try:
        process = CrawlerProcess(get_project_settings())
        process.crawl(spider_cls)
        process.start(stop_after_crawl=True)
        return True
    except Exception as e:
        logger.error(f"Spider {spider_cls.__name__} failed: {e}")
        return False


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_upsc_scraper(self):
    """Run UPSC scraper (every 2 hours)."""
    success = run_spider(UPSCScraper)
    if not success:
        raise self.retry(exc=Exception("UPSC scraper failed"))
    return {"status": "success", "spider": "upsc"}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_ssc_scraper(self):
    """Run SSC scraper (every 2 hours)."""
    success = run_spider(SSCScraper)
    if not success:
        raise self.retry(exc=Exception("SSC scraper failed"))
    return {"status": "success", "spider": "ssc"}
