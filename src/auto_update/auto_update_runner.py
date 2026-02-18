"""
Auto-Update Runner

ASSUMPTIONS:
- monitoring_config contains URLs to monitor
- change_detection + verification modules available

CONDITIONS:
- Database available
- URLs accessible

FAILURE MODES:
- URL fetch fails → skip
- Detection fails → ignore
"""

import os
import logging
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from src.auto_update.change_detection import detect_change
from src.auto_update.verification import should_auto_approve
from src.auto_update.status_propagation import propagate_status_change, send_admin_alert

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")


def run_auto_update_checks():
    if not DATABASE_URL:
        logger.error("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    try:
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT id, exam_id, urls_to_monitor, last_content_hash
                FROM monitoring_config
                WHERE is_active = true
            """)).fetchall()

            for row in rows:
                config_id, exam_id, urls, last_hash = row

                for url in urls:
                    try:
                        resp = requests.get(url, timeout=20)
                        if resp.status_code != 200:
                            continue

                        new_content = resp.text
                        change = detect_change(None, new_content)
                        if not change:
                            continue

                        confidence = change["confidence"]
                        approved = should_auto_approve(url, confidence, confirmations=1)

                        if approved:
                            propagate_status_change(exam_id, change["change_type"], change["context"], url)
                            send_admin_alert(exam_id, "active", change["change_type"], url)

                    except Exception as e:
                        logger.error(f"Auto-update check failed for {url}: {e}")

    except SQLAlchemyError as e:
        logger.error(f"DB error in auto-update runner: {e}")
