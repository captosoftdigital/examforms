"""
Status Propagation & Alert Hooks

ASSUMPTIONS:
- Exam status changes must propagate to all related pages
- Admin should be alerted on any status change

CONDITIONS:
- Exam exists in database
- Status change is approved

FAILURE MODES:
- DB update fails → log and return False
- Alert sending fails → log but do not rollback
"""

import json
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")


def propagate_status_change(exam_id: int, new_status: str, reason: str, source_url: str) -> bool:
    if not DATABASE_URL:
        logger.error("DATABASE_URL not set")
        return False

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.begin() as conn:
            # Update exam status
            conn.execute(text("""
                UPDATE exams
                SET status = :status,
                    status_reason = :reason,
                    status_updated_at = :updated_at,
                    status_source_url = :source_url
                WHERE id = :exam_id
            """), {
                "status": new_status,
                "reason": reason,
                "updated_at": datetime.utcnow(),
                "source_url": source_url,
                "exam_id": exam_id
            })

            # Mark pages for regeneration
            conn.execute(text("""
                UPDATE page_metadata
                SET needs_regeneration = true,
                    updated_at = NOW()
                WHERE exam_id = :exam_id
            """), {"exam_id": exam_id})

        return True

    except SQLAlchemyError as e:
        logger.error(f"Failed to propagate status: {e}")
        return False


def send_admin_alert(exam_id: int, old_status: str, new_status: str, source_url: str):
    """
    Placeholder for admin alerting.
    In production, integrate email/SMS/Slack.
    """
    logger.info(
        f"ALERT: Exam {exam_id} status changed {old_status} → {new_status}. Source: {source_url}"
    )
