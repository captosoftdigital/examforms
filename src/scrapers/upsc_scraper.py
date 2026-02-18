"""
UPSC Scraper - Union Public Service Commission
URL: https://upsc.gov.in
"""

import scrapy
from datetime import datetime
from .base_scraper import BaseExamScraper


class UPSCScraper(BaseExamScraper):
    """
    Scraper for UPSC exams
    Covers: Civil Services, CAPF, CDS, NDA, Engineering Services, etc.
    """
    
    name = 'upsc'
    exam_organization = 'Union Public Service Commission (UPSC)'
    exam_category = 'Central Government'
    
    start_urls = [
        'https://upsc.gov.in/examinations/current-examinations',
        'https://upsc.gov.in/examinations/admit-cards',
        'https://upsc.gov.in/examinations/results'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'USER_AGENT': 'Mozilla/5.0 (compatible; ExamFormsBot/1.0)',
        'ROBOTSTXT_OBEY': False,
    }
    
    def parse(self, response):
        """
        Parse UPSC main pages
        """
        self.logger.info(f"Parsing URL: {response.url}")
        # Extract notification links
        if 'current-examinations' in response.url:
            self.logger.info("Detected current-examinations page")
            yield from self.parse_notifications(response)
        
        # Extract admit card links
        elif 'admit-cards' in response.url:
            self.logger.info("Detected admit-cards page")
            yield from self.parse_admit_cards(response)
        
        # Extract result links
        elif 'results' in response.url:
            self.logger.info("Detected results page")
            yield from self.parse_results(response)
        else:
            self.logger.warning(f"Unrecognized URL: {response.url}")
    
    def parse_notifications(self, response):
        """
        Parse notification page
        """
        self.logger.info(f"Page Title: {response.css('title::text').get()}")
        # Example: Extract notification items
        notifications = response.css('.notification-item, .exam-notification')
        self.logger.info(f"Found {len(notifications)} notifications")
        
        # Try generic table rows if specific classes fail
        if len(notifications) == 0:
            self.logger.info("Trying generic table rows...")
            notifications = response.css('table tr')
            self.logger.info(f"Found {len(notifications)} table rows")

        for notif in notifications:
            exam_name = self.clean_text(notif.css('.title::text, h3::text').get())
            pdf_link = notif.css('a::attr(href)').get()
            date_text = notif.css('.date::text, .published-date::text').get()
            
            if exam_name and pdf_link:
                # Make absolute URL
                pdf_link = response.urljoin(pdf_link)
                
                notification_data = {
                    'exam_name': exam_name,
                    'pdf_link': pdf_link,
                    'notification_date': self.extract_date(date_text) if date_text else None,
                    'year': datetime.now().year,  # Extract from exam_name ideally
                }
                
                yield self.parse_notification(response, **notification_data)
    
    def parse_admit_cards(self, response):
        """
        Parse admit card listings
        """
        admit_cards = response.css('.admit-card-item, .hall-ticket')
        
        for card in admit_cards:
            exam_name = self.clean_text(card.css('.title::text, h3::text').get())
            download_link = card.css('a::attr(href)').get()
            date_text = card.css('.date::text').get()
            
            if exam_name and download_link:
                download_link = response.urljoin(download_link)
                
                admit_card_data = {
                    'exam_name': exam_name,
                    'download_link': download_link,
                    'release_date': self.extract_date(date_text) if date_text else None,
                    'year': datetime.now().year
                }
                
                yield self.parse_admit_card(response, **admit_card_data)
    
    def parse_results(self, response):
        """
        Parse result listings
        """
        results = response.css('.result-item, .exam-result')
        
        for result in results:
            exam_name = self.clean_text(result.css('.title::text, h3::text').get())
            result_link = result.css('a::attr(href)').get()
            date_text = result.css('.date::text').get()
            
            if exam_name and result_link:
                result_link = response.urljoin(result_link)
                
                result_data = {
                    'exam_name': exam_name,
                    'result_link': result_link,
                    'pdf_link': result_link,
                    'result_date': self.extract_date(date_text) if date_text else None,
                    'year': datetime.now().year
                }
                
                yield self.parse_result(response, **result_data)
