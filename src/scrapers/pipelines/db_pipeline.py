import re
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Django Setup (if needed, though usually handled by runner)
import django
from django.utils.text import slugify
from django.db import transaction, IntegrityError

from core_admin.models import Exam, ExamEvent, ScraperLog


class DatabasePipeline:
    """
    Pipeline to persist scraped items into PostgreSQL using Django ORM.
    Handles validation, duplicate detection, and safe failures.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Ensure Django is initialized if running standalone
        if not os.environ.get('DJANGO_SETTINGS_MODULE'):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
            try:
                django.setup()
            except Exception as e:
                self.logger.error(f"Django setup failed: {e}")

    def process_item(self, item: Dict[str, Any], spider=None):
        """
        Process a single scraped item using Django ORM.
        """
        if not item:
            return item

        if not item.get('exam_name') or not item.get('organization'):
            self.logger.warning(f"Missing mandatory fields in item from {spider.name if spider else 'unknown'}, skipping")
            self._save_backup(item, reason="missing_mandatory_fields")
            return item

        try:
            with transaction.atomic():
                event_type = item.get('event_type', 'notification')
                year = self._infer_year(item)

                # Get or create Exam
                exam = self._get_or_create_exam(item)

                # Get or create ExamEvent (duplicate detection based on exam, year, type)
                event, created = ExamEvent.objects.update_or_create(
                    exam=exam,
                    year=year,
                    event_type=event_type,
                    defaults={
                        'event_date': item.get('notification_date') or item.get('result_date'),
                        'application_start': item.get('application_start'),
                        'application_end': item.get('application_end'),
                        'exam_date': item.get('exam_date'),
                        'status': item.get('status', 'upcoming'),
                        'official_link': item.get('official_link') or item.get('source_url'),
                        'pdf_link': item.get('pdf_link'),
                        'download_link': item.get('download_link'),
                        'total_vacancies': item.get('total_vacancies'),
                        'details': item,  # JSONField handles dict automatically
                    }
                )

                if created:
                    self.logger.info(f"Created new {event_type} for {exam.name} ({year})")
                else:
                    self.logger.info(f"Updated existing {event_type} for {exam.name} ({year})")

            return item

        except IntegrityError as e:
            self.logger.error(f"Integrity error: {e}")
            self._save_backup(item, reason="integrity_error")
            return item
        except Exception as e:
            self.logger.error(f"Unexpected error in pipeline: {e}")
            self._save_backup(item, reason="unexpected_error")
            return item

    def _infer_year(self, item: Dict[str, Any]) -> int:
        """Infer year from item or use current year."""
        year = item.get('year')
        if year and isinstance(year, int):
            return year
        # Try to extract year from dates if available
        for field in ['notification_date', 'exam_date', 'result_date']:
            val = item.get(field)
            if val and isinstance(val, str) and len(val) >= 4:
                match = re.search(r'\d{4}', val)
                if match:
                    return int(match.group(0))
        return datetime.now().year

    def _get_or_create_exam(self, item: Dict[str, Any]) -> Exam:
        """Get existing exam or create a new one using Django ORM."""
        exam_name = item['exam_name'].strip()
        organization = item['organization'].strip()
        slug = slugify(exam_name)

        exam, created = Exam.objects.get_or_create(
            slug=slug,
            defaults={
                'name': exam_name,
                'organization': organization,
                'category': item.get('category', 'Central Government'),
                'exam_type': item.get('exam_type', 'Recruitment'),
                'is_active': True
            }
        )
        return exam

    def _save_backup(self, item: Dict[str, Any], reason: str):
        """Save failed item to disk for recovery."""
        backup_dir = os.path.join(os.getcwd(), 'backup_scraper_data')
        os.makedirs(backup_dir, exist_ok=True)

        filename = f"backup_{reason}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(backup_dir, filename)

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(item, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to write backup file: {e}")

    def open_spider(self, spider):
        """Log start of scraping"""
        self.logger.info(f"Spider opened: {spider.name}")

    def close_spider(self, spider):
        """Log completion of scraping"""
        self.logger.info(f"Spider closed: {spider.name}")

