# Scraper Scheduling Specifications

## Assumptions (Before Code)

1. Celery + Redis will be available for task scheduling.
2. Scrapy spiders can be invoked from Celery tasks via CrawlerProcess.
3. Scrapers must not overlap for the same source (avoid duplicate runs).
4. UPSC/SSC require higher frequency (every 2 hours).
5. Failures should not stop the scheduler.

## Conditions for Success
- Redis reachable
- Celery worker running
- Scrapy can run in isolated process
- Tasks complete within configured timeouts

## Failure Modes
- Redis down → tasks queue fails (log, alert)
- Scraper crash → task catches exception, logs failure
- Task overlap → prevented by lock
- Long runtime → task times out gracefully

