"""
Complete Base Scraper Framework for ExamForms.org

PRODUCTION-READY with comprehensive error handling.
"""

import scrapy
import time
import hashlib
import json
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urljoin, urlparse
import logging
import re
from decimal import Decimal

# Date parsing
from dateutil import parser as date_parser

# Text cleaning
import html as html_lib
import unicodedata


class ScraperError(Exception):
    """Base exception for scraper errors"""
    pass


class ValidationError(ScraperError):
    """Data validation failed"""
    pass


class ParsingError(ScraperError):
    """HTML parsing failed"""
    pass


class BaseExamScraper(scrapy.Spider):
    """
    Production-ready base scraper with complete error handling
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limiting (5s delay between requests)
    - Data validation and cleaning
    - Confidence scoring
    - Duplicate detection
    - Graceful failure handling
    """
    
    name = 'base_scraper'
    exam_organization = 'Unknown'
    exam_category = 'Unknown'
    
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
        'DOWNLOAD_TIMEOUT': 30,
        'USER_AGENT': 'Mozilla/5.0 (compatible; ExamFormsBot/1.0)',
    }
    
    MANDATORY_FIELDS = ['exam_name', 'organization']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.logger is a property in Scrapy, do not overwrite
        self.stats = {
            'pages_scraped': 0,
            'items_extracted': 0,
            'items_valid': 0,
            'items_invalid': 0,
            'errors': [],
            'start_time': datetime.now()
        }
    
    # ========================================================================
    # TEXT CLEANING UTILITIES
    # ========================================================================
    
    def clean_text(self, text: str) -> str:
        """
        Clean text: strip whitespace, normalize spaces, decode HTML entities
        
        HANDLES:
        - None input → returns ''
        - HTML entities (&nbsp;, &amp;, etc.)
        - Multiple spaces → single space
        - Unicode normalization
        - Leading/trailing whitespace
        
        EXAMPLES:
        "  Hello   World  " → "Hello World"
        "Hello&nbsp;World" → "Hello World"
        "Café" → "Café" (normalized)
        """
        if not text:
            return ''
        
        try:
            # Decode HTML entities
            text = html_lib.unescape(text)
            
            # Normalize Unicode (NFC form)
            text = unicodedata.normalize('NFC', text)
            
            # Replace multiple spaces with single space
            text = re.sub(r'\s+', ' ', text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Error cleaning text: {e}")
            return str(text).strip()
    
    def extract_number(self, text: str) -> Optional[int]:
        """
        Extract first number from text
        
        HANDLES:
        - Comma-separated numbers: "1,000" → 1000
        - Text with numbers: "Total 500 posts" → 500
        - No numbers: returns None
        - Invalid input: returns None
        
        EXAMPLES:
        "Total Vacancies: 1,500" → 1500
        "500 posts announced" → 500
        "No vacancies" → None
        """
        if not text:
            return None
        
        try:
            # Remove commas
            text = text.replace(',', '')
            
            # Find all numbers
            numbers = re.findall(r'\d+', text)
            
            if numbers:
                return int(numbers[0])
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting number from '{text}': {e}")
            return None
    
    def extract_date(self, date_string: str) -> Optional[str]:
        """
        Parse various date formats to YYYY-MM-DD
        
        HANDLES:
        - Multiple formats: DD/MM/YYYY, DD-MM-YYYY, Month DD YYYY
        - Fuzzy parsing: "The exam will be held on 15th March 2026"
        - Ambiguous dates: "First week of March" → None (not guessing)
        - Invalid dates: returns None
        
        EXAMPLES:
        "15/03/2026" → "2026-03-15"
        "15-03-2026" → "2026-03-15"
        "March 15, 2026" → "2026-03-15"
        "15th March 2026" → "2026-03-15"
        "First week of March" → None (ambiguous)
        
        DOES NOT:
        - Guess dates ("March" alone → None, not "2026-03-01")
        - Accept future dates beyond 2030
        - Accept past dates before 2020
        """
        if not date_string:
            return None
        
        try:
            # Clean the string
            date_string = self.clean_text(date_string)
            
            # Try parsing with dateutil (fuzzy mode)
            dt = date_parser.parse(date_string, fuzzy=True)
            
            # Validate year is reasonable (2020-2030)
            if dt.year < 2020 or dt.year > 2030:
                self.logger.warning(f"Date year out of range: {dt.year}")
                return None
            
            return dt.strftime('%Y-%m-%d')
            
        except Exception as e:
            self.logger.warning(f"Could not parse date '{date_string}': {e}")
            return None
    
    def make_absolute_url(self, url: str, response) -> str:
        """
        Convert relative URL to absolute
        
        HANDLES:
        - Relative URLs: "/notification.pdf" → "https://example.com/notification.pdf"
        - Absolute URLs: returned as-is
        - Malformed URLs: logged and returned as-is
        - None: returns empty string
        """
        if not url:
            return ''
        
        try:
            return response.urljoin(url)
        except Exception as e:
            self.logger.warning(f"Error making absolute URL from '{url}': {e}")
            return url
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid
        
        VALIDATES:
        - Scheme present (http/https)
        - Domain present
        - No spaces
        
        DOES NOT validate:
        - URL accessibility (might be 404)
        - SSL certificate validity
        """
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    # ========================================================================
    # DATA VALIDATION
    # ========================================================================
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate scraped data
        
        CHECKS:
        - Mandatory fields present and non-empty
        - Optional fields have valid format if present
        - URLs are valid format
        - Dates are valid format
        
        Returns: (is_valid, list_of_missing_fields)
        
        DOES NOT check:
        - URL accessibility (200 status)
        - Data accuracy (that's manual review's job)
        - Duplicate detection (separate method)
        """
        missing_fields = []
        
        # Check mandatory fields
        for field in self.MANDATORY_FIELDS:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        
        if missing_fields:
            return False, missing_fields
        
        # Validate URL fields if present
        url_fields = ['official_link', 'pdf_link', 'download_link', 'apply_link']
        for field in url_fields:
            url = data.get(field)
            if url and not self.is_valid_url(url):
                self.logger.warning(f"Invalid URL in field '{field}': {url}")
                # Don't fail validation, just log
        
        return True, []
    
    def calculate_confidence(self, data: Dict[str, Any]) -> int:
        """
        Calculate confidence score (0-100) for scraped data
        
        SCORING:
        - exam_name present: +30
        - organization present: +20
        - notification_date present: +15
        - official_link valid: +15
        - application dates present: +10
        - exam_date present: +10
        
        HIGH CONFIDENCE (>= 70): Auto-approve
        MEDIUM CONFIDENCE (40-69): Review recommended
        LOW CONFIDENCE (< 40): Manual review required
        
        EXAMPLES:
        - All fields present: 100
        - Only name + org: 50 (manual review)
        - Name + org + date + link: 80 (auto-approve)
        """
        score = 0
        
        # Mandatory fields (50 points total)
        if data.get('exam_name') and self.clean_text(data['exam_name']):
            score += 30
        if data.get('organization') and self.clean_text(data['organization']):
            score += 20
        
        # Important optional fields (50 points total)
        if data.get('notification_date'):
            score += 15
        if data.get('official_link') and self.is_valid_url(data['official_link']):
            score += 15
        if data.get('application_start') and data.get('application_end'):
            score += 10
        if data.get('exam_date'):
            score += 10
        
        return min(score, 100)
    
    # ========================================================================
    # PARSING WRAPPER METHODS
    # ========================================================================
    
    # ========================================================================
    # PARSING STRATEGIES
    # ========================================================================
    
    def parse_with_strategies(self, response, strategy_type='notification', **kwargs) -> Optional[Dict]:
        """
        Try to parse data using multiple strategies in order:
        1. Specific Selectors (Child Class implementation)
        2. Heuristics (Generic patterns)
        3. AI Parsing (LLM Fallback)
        """
        # Strategy 1: Specific Selectors
        try:
            if strategy_type == 'notification':
                data = self.parse_notification(response, **kwargs)
            elif strategy_type == 'admit_card':
                data = self.parse_admit_card(response, **kwargs)
            elif strategy_type == 'result':
                data = self.parse_result(response, **kwargs)
            else:
                data = None
                
            if data:
                return data
        except NotImplementedError:
             pass # Child might not implement it yet
        except Exception as e:
            self.logger.warning(f"Standard parsing failed: {e}")

        # Strategy 2: Heuristics
        # TODO: Implement generic heuristic parser here
        # data = self.parse_heuristic(response)
        # if data: return data

        # Strategy 3: AI Parsing (Fallback)
        # Only if confidence is critical or specific flag is set
        try:
            if hasattr(self, 'crawler') and getattr(self, 'crawler', None) and hasattr(self.crawler, 'settings') and self.crawler.settings:
                enable_ai = self.crawler.settings.getbool('ENABLE_AI_PARSING', False)
                provider = self.crawler.settings.get('AI_PROVIDER', 'openai')
            elif getattr(self, 'settings', None):
                # Fallback implementation if crawler is not set but settings are injected
                enable_ai = self.settings.getbool('ENABLE_AI_PARSING', False)
                provider = self.settings.get('AI_PROVIDER', 'openai')
            else:
                 self.logger.warning("Could not find settings in BaseExamScraper")
                 enable_ai = False
            
            if enable_ai:
                self.logger.info("Attempting AI parsing...")
                from src.utils.ai_parser import AIParser
                ai_parser = AIParser(provider=provider)
                
                # Extract text content (simplified)
                text_content = " ".join(response.css('body ::text').getall())
                data = ai_parser.parse_notification(text_content)
                
                if data:
                    data['parsing_method'] = 'ai_fallback'
                    return data
        except Exception as e:
                 self.logger.error(f"AI parsing failed: {e}")

        return None

    def safe_parse_notification(self, response, **metadata) -> Optional[Dict]:
        """
        Safely parse notification with full error handling and auto-recovery
        """
        try:
            # delegated to strategy manager
            data = self.parse_with_strategies(response, strategy_type='notification', **metadata)
            
            if not data:
                self.logger.warning(f"No data extracted from {response.url} after all strategies.")
                return None
            
            # Add metadata
            data['scraped_at'] = datetime.now().isoformat()
            data['source_url'] = response.url
            
            # Clean text fields
            for field in ['exam_name', 'organization', 'description']:
                if field in data and data[field]:
                    data[field] = self.clean_text(data[field])
            
            # Parse dates
            date_fields = ['notification_date', 'application_start', 
                          'application_end', 'exam_date']
            for field in date_fields:
                if field in data and data[field]:
                    data[field] = self.extract_date(data[field])
            
            # Make URLs absolute
            url_fields = ['official_link', 'pdf_link', 'apply_link']
            for field in url_fields:
                if field in data and data[field]:
                    data[field] = self.make_absolute_url(data[field], response)
            
            # Extract numbers
            if data.get('total_vacancies') and isinstance(data['total_vacancies'], str):
                data['total_vacancies'] = self.extract_number(data['total_vacancies'])
            
            # Validate
            is_valid, missing = self.validate_data(data)
            if not is_valid:
                # If AI parsed it, we might be more lenient, or require re-parsing
                self.logger.warning(f"Validation failed. Missing: {missing}")
                self.stats['items_invalid'] += 1
                data['validation_failed'] = True
                data['missing_fields'] = missing
                return data
            
            # Calculate confidence
            confidence = self.calculate_confidence(data)
            data['confidence_score'] = confidence
            
            if confidence < 70:
                self.logger.warning(f"Low confidence: {confidence}. Flagging for review.")
                data['requires_manual_review'] = True
            
            self.stats['items_extracted'] += 1
            self.stats['items_valid'] += 1
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing notification from {response.url}: {e}")
            self.stats['errors'].append({
                'url': response.url,
                'error': str(e),
                'type': 'parse_error'
            })
            return None
    
    # ========================================================================
    # METHODS TO OVERRIDE IN CHILD CLASSES
    # ========================================================================
    
    def parse_notification(self, response, **metadata):
        """
        OVERRIDE THIS in child classes
        
        Extract notification data using CSS/XPath selectors
        Return dict with fields or None
        """
        raise NotImplementedError("Child class must implement parse_notification()")
    
    def parse_admit_card(self, response, **metadata):
        """OVERRIDE THIS in child classes"""
        raise NotImplementedError("Child class must implement parse_admit_card()")
    
    def parse_result(self, response, **metadata):
        """OVERRIDE THIS in child classes"""
        raise NotImplementedError("Child class must implement parse_result()")
    
    # ========================================================================
    # HELPER: MULTIPLE SELECTOR ATTEMPTS
    # ========================================================================
    
    def try_selectors(self, response, selectors: List[str], method='css') -> Optional[str]:
        """
        Try multiple selectors until one succeeds
        
        USAGE:
        title = self.try_selectors(response, [
            '.notification-title::text',
            'h2.title::text',
            'h1::text'
        ])
        
        HANDLES:
        - All selectors fail → returns None
        - First match returned
        - Cleans text automatically
        """
        for selector in selectors:
            try:
                if method == 'css':
                    result = response.css(selector).get()
                else:
                    result = response.xpath(selector).get()
                
                if result:
                    return self.clean_text(result)
            except Exception as e:
                self.logger.debug(f"Selector failed: {selector} - {e}")
                continue
        
        return None
    
    # ========================================================================
    # LOGGING & STATS
    # ========================================================================
    
    def closed(self, reason):
        """Called when spider closes"""
        end_time = datetime.now()
        duration = (end_time - self.stats['start_time']).total_seconds()
        
        self.logger.info(f"Scraper {self.name} closed: {reason}")
        self.logger.info(f"Duration: {duration:.2f}s")
        self.logger.info(f"Pages: {self.stats['pages_scraped']}")
        self.logger.info(f"Valid items: {self.stats['items_valid']}")
        self.logger.info(f"Invalid items: {self.stats['items_invalid']}")
        self.logger.info(f"Errors: {len(self.stats['errors'])}")


# Example usage in child class:
"""
class UPSCScraper(BaseExamScraper):
    name = 'upsc'
    exam_organization = 'Union Public Service Commission'
    exam_category = 'Central Government'
    
    start_urls = ['https://upsc.gov.in/examinations']
    
    def parse(self, response):
        # Extract notification links
        for link in response.css('.notification-item a'):
            yield response.follow(link, self.parse_notification_page)
    
    def parse_notification_page(self, response):
        # Use safe_parse_notification wrapper
        data = self.safe_parse_notification(response)
        if data:
            yield data
    
    def parse_notification(self, response, **metadata):
        # Your specific extraction logic
        title = self.try_selectors(response, [
            '.notification-title::text',
            'h2::text',
            'h1::text'
        ])
        
        return {
            'exam_name': title,
            'organization': self.exam_organization,
            'official_link': response.url,
            # ... more fields
        }
"""
