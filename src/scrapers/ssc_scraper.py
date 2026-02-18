"""
SSC Scraper - Staff Selection Commission
URL: https://ssc.nic.in
"""

import scrapy
from datetime import datetime
from .base_scraper import BaseExamScraper


class SSCScraper(BaseExamScraper):
    """
    Scraper for SSC exams
    Covers: CGL, CHSL, MTS, JE, CPO, Stenographer, GD Constable
    """
    
    name = 'ssc'
    exam_organization = 'Staff Selection Commission (SSC)'
    exam_category = 'Central Government'
    
    start_urls = [
        'https://ssc.nic.in/Portal/LatestNotification',
        'https://ssc.nic.in/Portal/AdmitCard',
        'https://ssc.nic.in/Portal/Results'
    ]
    
    # SSC regional websites
    regional_urls = [
        'https://ssc-cr.org',
        'https://ssc-wr.org',
        'https://sscner.org.in',
        'https://sscsr.gov.in',
        # Add other regional sites
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'USER_AGENT': 'Mozilla/5.0 (compatible; ExamFormsBot/1.0)'
    }
    
    def parse(self, response):
        """
        Parse SSC pages
        """
        if 'LatestNotification' in response.url:
            yield from self.parse_notifications(response)
        elif 'AdmitCard' in response.url:
            yield from self.parse_admit_cards(response)
        elif 'Results' in response.url:
            yield from self.parse_results(response)
    
    def parse_notifications(self, response):
        """
        Parse SSC notification page
        """
        # SSC usually has table structure
        rows = response.css('table tr, .notification-row')
        
        for row in rows[1:]:  # Skip header row
            cells = row.css('td')
            
            if len(cells) >= 2:
                exam_name = self.clean_text(cells[0].css('::text').get())
                pdf_link = cells[1].css('a::attr(href)').get()
                date_text = cells[2].css('::text').get() if len(cells) > 2 else None
                
                if exam_name and pdf_link:
                    pdf_link = response.urljoin(pdf_link)
                    
                    notification_data = {
                        'exam_name': exam_name,
                        'pdf_link': pdf_link,
                        'notification_date': self.extract_date(date_text) if date_text else None,
                        'year': datetime.now().year
                    }
                    
                    yield self.parse_notification(response, **notification_data)
    
    def parse_admit_cards(self, response):
        """
        Parse SSC admit card page
        """
        rows = response.css('table tr, .admit-card-row')
        
        for row in rows[1:]:
            cells = row.css('td')
            
            if len(cells) >= 2:
                exam_name = self.clean_text(cells[0].css('::text').get())
                download_link = cells[1].css('a::attr(href)').get()
                
                if exam_name and download_link:
                    download_link = response.urljoin(download_link)
                    
                    admit_card_data = {
                        'exam_name': exam_name,
                        'download_link': download_link,
                        'year': datetime.now().year
                    }
                    
                    yield self.parse_admit_card(response, **admit_card_data)
    
    def parse_results(self, response):
        """
        Parse SSC result page
        """
        rows = response.css('table tr, .result-row')
        
        for row in rows[1:]:
            cells = row.css('td')
            
            if len(cells) >= 2:
                exam_name = self.clean_text(cells[0].css('::text').get())
                result_link = cells[1].css('a::attr(href)').get()
                date_text = cells[2].css('::text').get() if len(cells) > 2 else None
                
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
