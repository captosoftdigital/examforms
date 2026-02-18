"""
SSC Scraper - Staff Selection Commission

PRODUCTION-READY scraper for SSC exams with complete error handling.

TARGET: https://ssc.nic.in
PAGES: Notifications, Admit Cards, Results

ASSUMPTIONS:
- Official SSC portal is authoritative
- HTML structure may change (fallback selectors in place)
- Dates may be missing or inconsistent
- Regional sites may differ

CONDITIONS FOR SUCCESS:
- SSC site returns HTTP 200
- Exam name + organization extracted
- Network timeout < 30 seconds

FAILURE MODES:
- Selector failure → manual review
- Timeout → retry and skip
- Missing mandatory fields → partial save + flag
"""

import scrapy
from datetime import datetime
import re
from typing import Dict, Any, Optional, List
from base_scraper_complete import BaseExamScraper


class SSCScraper(BaseExamScraper):
    """
    Staff Selection Commission scraper

    Scrapes:
    - Latest notifications
    - Admit cards
    - Results
    """

    name = 'ssc'
    exam_organization = 'Staff Selection Commission (SSC)'
    exam_category = 'Central Government'

    start_urls = [
        'https://ssc.nic.in/Portal/LatestNotification',
        'https://ssc.nic.in/Portal/AdmitCard',
        'https://ssc.nic.in/Portal/Results',
    ]

    regional_urls = [
        'https://ssc-cr.org',
        'https://ssc-wr.org',
        'https://sscner.org.in',
        'https://sscsr.gov.in',
    ]

    # SSC pages can be slow
    custom_settings = {
        **BaseExamScraper.custom_settings,
        'DOWNLOAD_TIMEOUT': 45,
    }

    # Selector mappings
    TITLE_SELECTORS = [
        'table tr td:first-child::text',
        '.notification-title::text',
        'h2::text',
        'h3::text',
        'a::text',
    ]

    DATE_SELECTORS = [
        'table tr td:nth-child(2)::text',
        '.date::text',
        'span.date::text',
    ]

    LINK_SELECTORS = [
        'a[href$=".pdf"]::attr(href)',
        'a[href*=".pdf"]::attr(href)',
        'a::attr(href)',
    ]

    def parse(self, response):
        """Route to the correct parser based on URL"""
        if 'LatestNotification' in response.url:
            yield from self.parse_notifications_page(response)
        elif 'AdmitCard' in response.url:
            yield from self.parse_admit_cards_page(response)
        elif 'Results' in response.url:
            yield from self.parse_results_page(response)
        else:
            self.logger.warning(f"Unknown page type: {response.url}")

    # ========================================================================
    # NOTIFICATIONS
    # ========================================================================

    def parse_notifications_page(self, response):
        """Parse SSC notifications page"""
        rows = response.css('table tr')

        if not rows:
            rows = response.css('.notification-item')

        if not rows:
            self.logger.warning(f"No notifications found on {response.url}")
            return

        for row in rows[1:]:  # Skip header
            data = self._extract_notification_data(row, response)
            if data:
                result = self.safe_parse_notification(response, **data)
                if result:
                    yield result

    def _extract_notification_data(self, element, response) -> Optional[Dict]:
        """Extract notification data from a table row or item"""
        title = self.try_selectors(element, self.TITLE_SELECTORS)
        if not title:
            return None

        date_text = self.try_selectors(element, self.DATE_SELECTORS)
        pdf_link = self.try_selectors(element, self.LINK_SELECTORS)

        return {
            'exam_name': title,
            'organization': self.exam_organization,
            'notification_date': date_text,
            'pdf_link': pdf_link,
        }

    def parse_notification(self, response, **metadata):
        """Override for base class"""
        return metadata

    # ========================================================================
    # ADMIT CARDS
    # ========================================================================

    def parse_admit_cards_page(self, response):
        rows = response.css('table tr')

        if not rows:
            rows = response.css('.admit-card-item')

        if not rows:
            self.logger.warning(f"No admit cards found on {response.url}")
            return

        for row in rows[1:]:
            data = self._extract_admit_card_data(row, response)
            if data:
                result = self.safe_parse_admit_card(response, **data)
                if result:
                    yield result

    def _extract_admit_card_data(self, element, response) -> Optional[Dict]:
        title = self.try_selectors(element, self.TITLE_SELECTORS)
        if not title:
            return None

        date_text = self.try_selectors(element, self.DATE_SELECTORS)
        download_link = self.try_selectors(element, self.LINK_SELECTORS)

        return {
            'exam_name': title,
            'organization': self.exam_organization,
            'release_date': date_text,
            'download_link': download_link,
        }

    def parse_admit_card(self, response, **metadata):
        return metadata

    # ========================================================================
    # RESULTS
    # ========================================================================

    def parse_results_page(self, response):
        rows = response.css('table tr')

        if not rows:
            rows = response.css('.result-item')

        if not rows:
            self.logger.warning(f"No results found on {response.url}")
            return

        for row in rows[1:]:
            data = self._extract_result_data(row, response)
            if data:
                result = self.safe_parse_result(response, **data)
                if result:
                    yield result

    def _extract_result_data(self, element, response) -> Optional[Dict]:
        title = self.try_selectors(element, self.TITLE_SELECTORS)
        if not title:
            return None

        date_text = self.try_selectors(element, self.DATE_SELECTORS)
        result_link = self.try_selectors(element, self.LINK_SELECTORS)

        stage = None
        if 'tier' in title.lower():
            stage = 'Tier'
        elif 'final' in title.lower():
            stage = 'Final'

        return {
            'exam_name': title,
            'organization': self.exam_organization,
            'result_date': date_text,
            'result_link': result_link,
            'pdf_link': result_link,
            'stage': stage,
        }

    def parse_result(self, response, **metadata):
        return metadata

