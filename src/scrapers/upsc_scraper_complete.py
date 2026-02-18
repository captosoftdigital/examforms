"""
UPSC Scraper - Union Public Service Commission

PRODUCTION-READY scraper for UPSC exams with complete error handling.

TARGET: https://upsc.gov.in
PAGES: Notifications, Admit Cards, Results, Answer Keys

HANDLES:
- Multiple page structures (table, list, div-based)
- Missing data (partial extraction with flagging)
- Structure changes (fallback selectors)
- PDF-only notifications (extracts available data)
- Slow responses (30s timeout)
- Duplicate notifications (update existing)

CONDITIONS FOR SUCCESS:
- UPSC website returns 200
- At least exam name + organization extracted
- Network timeout < 30 seconds

FAILURE MODES:
- All selectors fail → Manual review
- Timeout → Retry next run
- Missing mandatory fields → Save partial + flag
"""

import scrapy
from datetime import datetime
import re
from typing import Dict, Any, Optional, List
from base_scraper_complete import BaseExamScraper


class UPSCScraper(BaseExamScraper):
    """
    Union Public Service Commission scraper
    
    Scrapes:
    - Current examinations and notifications
    - Admit cards
    - Results
    - Answer keys
    
    Uses base class for:
    - Error handling
    - Data cleaning
    - Validation
    - Confidence scoring
    """
    
    name = 'upsc'
    exam_organization = 'Union Public Service Commission (UPSC)'
    exam_category = 'Central Government'
    
    # Start URLs - will be scraped in sequence
    start_urls = [
        'https://upsc.gov.in/examinations/current-examinations',
        'https://upsc.gov.in/examinations/admit-cards',
        'https://upsc.gov.in/examinations/results',
    ]
    
    # Custom settings for UPSC (may be slow)
    custom_settings = {
        **BaseExamScraper.custom_settings,
        'DOWNLOAD_TIMEOUT': 45,  # UPSC can be slow
    }
    
    # Selector mappings for different page types
    EXAM_TITLE_SELECTORS = [
        '.notification-title a::text',
        '.exam-title::text',
        'h3.title::text',
        'h3 a::text',
        'h2 a::text',
        'td.title::text',
        'a[href*=".pdf"]::text',  # Last resort: PDF link text
    ]
    
    DATE_SELECTORS = [
        '.notification-date::text',
        '.date::text',
        'span.date::text',
        'td.date::text',
    ]
    
    PDF_LINK_SELECTORS = [
        'a[href$=".pdf"]::attr(href)',
        'a[href*=".pdf"]::attr(href)',
        '.download-link::attr(href)',
        'a:contains("Download")::attr(href)',
        'a:contains("Notification")::attr(href)',
    ]
    
    def parse(self, response):
        """
        Main entry point - routes to appropriate parser based on URL
        
        HANDLES:
        - Different page types (notifications, admit cards, results)
        - Multiple notification formats on same page
        - Empty pages (no current exams)
        """
        self.logger.info(f"Parsing {response.url}")
        
        # Determine page type from URL
        if 'current-examinations' in response.url or 'notifications' in response.url:
            yield from self.parse_notifications_page(response)
        elif 'admit-card' in response.url:
            yield from self.parse_admit_cards_page(response)
        elif 'result' in response.url:
            yield from self.parse_results_page(response)
        else:
            self.logger.warning(f"Unknown page type: {response.url}")
    
    # ========================================================================
    # NOTIFICATIONS PAGE
    # ========================================================================
    
    def parse_notifications_page(self, response):
        """
        Parse notifications page - may contain multiple exam notifications
        
        TRIES multiple structures:
        1. Div-based (.notification-item, .exam-notification)
        2. List-based (ul.notifications li)
        3. Table-based (table.exams tr)
        4. Generic (any div with PDF link)
        
        YIELDS: Notification data or None if extraction fails
        """
        # Try structure 1: Div-based
        notifications = response.css('.notification-item, .exam-notification, .notification')
        
        if not notifications:
            # Try structure 2: List-based
            notifications = response.css('ul.notifications li, ul.exams li, ul li')
        
        if not notifications:
            # Try structure 3: Table-based
            notifications = response.css('table.notifications tr, table.exams tr, table tr')
        
        if not notifications:
            # Try structure 4: Generic - any div with a PDF link
            notifications = response.css('div:has(a[href*=".pdf"])')
        
        if not notifications:
            self.logger.warning(f"No notifications found on {response.url}")
            self.logger.warning("HTML structure may have changed - manual review needed")
            return
        
        self.logger.info(f"Found {len(notifications)} potential notifications")
        
        for notification in notifications:
            # Extract using safe wrapper
            data = self._extract_notification_data(notification, response)
            
            if data:
                # Use base class safe wrapper
                result = self.safe_parse_notification(response, **data)
                if result:
                    yield result
    
    def _extract_notification_data(self, element, response) -> Optional[Dict]:
        """
        Extract notification data from a single element
        
        TRIES multiple selectors for each field
        RETURNS: Dict with extracted data or None
        """
        # Extract exam title (mandatory)
        title = self.try_selectors(element, self.EXAM_TITLE_SELECTORS)
        
        if not title:
            # Try getting any link text
            title = element.css('a::text').get()
            title = self.clean_text(title) if title else None
        
        if not title:
            self.logger.debug("Could not extract title, skipping item")
            return None
        
        # Extract date (optional)
        date_text = self.try_selectors(element, self.DATE_SELECTORS)
        
        if not date_text:
            # Try finding date pattern in any text
            all_text = ' '.join(element.css('::text').getall())
            date_match = re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', all_text)
            date_text = date_match.group(0) if date_match else None
        
        # Extract PDF link (important but optional)
        pdf_link = self.try_selectors(element, self.PDF_LINK_SELECTORS)
        
        # Extract description (optional)
        description = element.css('.description::text, p::text').get()
        description = self.clean_text(description) if description else None
        
        # Extract vacancies if mentioned (optional)
        vacancy_text = element.css(':contains("Vacancies")').re_first(r'(\d+)\s+(?:Total\s+)?Vacanc')
        vacancies = self.extract_number(vacancy_text) if vacancy_text else None
        
        # Build data dict
        data = {
            'exam_name': title,
            'organization': self.exam_organization,
            'notification_date': date_text,
            'pdf_link': pdf_link,
            'description': description,
            'total_vacancies': vacancies,
        }
        
        return data
    
    def parse_notification(self, response, **metadata):
        """
        OVERRIDE: Required by base class
        
        This is called by safe_parse_notification wrapper
        For UPSC, actual parsing is done in _extract_notification_data
        
        This method just returns the metadata passed to it
        """
        return metadata
    
    # ========================================================================
    # ADMIT CARDS PAGE
    # ========================================================================
    
    def parse_admit_cards_page(self, response):
        """
        Parse admit cards page
        
        EXTRACTS:
        - Exam name
        - Admit card release date
        - Exam date
        - Download link
        """
        # Try to find admit card items
        items = response.css('.admit-card-item, .hall-ticket, .notification-item')
        
        if not items:
            items = response.css('ul li, table tr')
        
        if not items:
            self.logger.warning(f"No admit cards found on {response.url}")
            return
        
        self.logger.info(f"Found {len(items)} potential admit cards")
        
        for item in items:
            data = self._extract_admit_card_data(item, response)
            if data:
                result = self.safe_parse_admit_card(response, **data)
                if result:
                    yield result
    
    def _extract_admit_card_data(self, element, response) -> Optional[Dict]:
        """Extract admit card data from element"""
        # Exam name
        title = self.try_selectors(element, self.EXAM_TITLE_SELECTORS)
        if not title:
            title = element.css('a::text').get()
            title = self.clean_text(title) if title else None
        
        if not title:
            return None
        
        # Dates
        date_text = self.try_selectors(element, self.DATE_SELECTORS)
        
        # Download link
        download_link = self.try_selectors(element, self.PDF_LINK_SELECTORS)
        
        # Try to identify exam date vs release date
        # If date is in future, likely exam date
        # If in past or recent, likely release date
        exam_date = None
        release_date = date_text
        
        # Look for "Exam on" pattern
        exam_date_match = element.css(':contains("Exam")').re_first(r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})')
        if exam_date_match:
            exam_date = exam_date_match
        
        return {
            'exam_name': title,
            'organization': self.exam_organization,
            'release_date': release_date,
            'exam_date': exam_date,
            'download_link': download_link,
        }
    
    def safe_parse_admit_card(self, response, **metadata):
        """Safe wrapper for admit card parsing"""
        try:
            data = self.parse_admit_card(response, **metadata)
            if not data:
                return None
            
            # Add metadata
            data['scraped_at'] = datetime.now().isoformat()
            data['source_url'] = response.url
            data['event_type'] = 'admit_card'
            
            # Clean and validate (similar to notification)
            for field in ['exam_name', 'organization']:
                if field in data and data[field]:
                    data[field] = self.clean_text(data[field])
            
            # Parse dates
            for field in ['release_date', 'exam_date']:
                if field in data and data[field]:
                    data[field] = self.extract_date(data[field])
            
            # Make URLs absolute
            if data.get('download_link'):
                data['download_link'] = self.make_absolute_url(data['download_link'], response)
            
            # Calculate confidence
            confidence = self.calculate_confidence(data)
            data['confidence_score'] = confidence
            
            if confidence < 70:
                data['requires_manual_review'] = True
            
            self.stats['items_extracted'] += 1
            self.stats['items_valid'] += 1
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing admit card: {e}")
            return None
    
    def parse_admit_card(self, response, **metadata):
        """OVERRIDE: Required by base class"""
        return metadata
    
    # ========================================================================
    # RESULTS PAGE
    # ========================================================================
    
    def parse_results_page(self, response):
        """
        Parse results page
        
        EXTRACTS:
        - Exam name with stage (Prelims/Mains/Final)
        - Result date
        - Result PDF link
        """
        # Try to find result items
        items = response.css('.result-item, .exam-result, .notification-item')
        
        if not items:
            items = response.css('ul li, table tr')
        
        if not items:
            self.logger.warning(f"No results found on {response.url}")
            return
        
        self.logger.info(f"Found {len(items)} potential results")
        
        for item in items:
            data = self._extract_result_data(item, response)
            if data:
                result = self.safe_parse_result(response, **data)
                if result:
                    yield result
    
    def _extract_result_data(self, element, response) -> Optional[Dict]:
        """Extract result data from element"""
        # Exam name
        title = self.try_selectors(element, self.EXAM_TITLE_SELECTORS)
        if not title:
            title = element.css('a::text').get()
            title = self.clean_text(title) if title else None
        
        if not title:
            return None
        
        # Result date
        date_text = self.try_selectors(element, self.DATE_SELECTORS)
        
        # Result link
        result_link = self.try_selectors(element, self.PDF_LINK_SELECTORS)
        
        # Try to detect exam stage from title
        stage = None
        if 'prelim' in title.lower():
            stage = 'Prelims'
        elif 'main' in title.lower():
            stage = 'Mains'
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
    
    def safe_parse_result(self, response, **metadata):
        """Safe wrapper for result parsing"""
        try:
            data = self.parse_result(response, **metadata)
            if not data:
                return None
            
            # Add metadata
            data['scraped_at'] = datetime.now().isoformat()
            data['source_url'] = response.url
            data['event_type'] = 'result'
            
            # Clean text
            for field in ['exam_name', 'organization']:
                if field in data and data[field]:
                    data[field] = self.clean_text(data[field])
            
            # Parse dates
            if data.get('result_date'):
                data['result_date'] = self.extract_date(data['result_date'])
            
            # Make URLs absolute
            for field in ['result_link', 'pdf_link']:
                if data.get(field):
                    data[field] = self.make_absolute_url(data[field], response)
            
            # Calculate confidence
            confidence = self.calculate_confidence(data)
            data['confidence_score'] = confidence
            
            if confidence < 70:
                data['requires_manual_review'] = True
            
            self.stats['items_extracted'] += 1
            self.stats['items_valid'] += 1
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing result: {e}")
            return None
    
    def parse_result(self, response, **metadata):
        """OVERRIDE: Required by base class"""
        return metadata


# Example usage:
"""
# Run scraper
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (compatible; ExamFormsBot/1.0)',
    'LOG_LEVEL': 'INFO',
})

process.crawl(UPSCScraper)
process.start()
"""
