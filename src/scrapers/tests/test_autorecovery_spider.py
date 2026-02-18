import scrapy
from src.scrapers.base_scraper_complete import BaseExamScraper

class TestAutoRecoverySpider(BaseExamScraper):
    name = "test_autorecovery"
    start_urls = ['https://example.com'] # Dummy URL
    
    custom_settings = {
        'ENABLE_AI_PARSING': True,
        'AI_PROVIDER': 'openai',
        'LOG_LEVEL': 'INFO'
    }

    def parse(self, response):
        # We need to simulate a response with some content
        # But for this test, let's just use the response as is 
        # and manually call safe_parse_notification
        
        # Inject dummy body content if needed for AI parser to "see" something
        response = response.replace(body=b"<html><body><h1>Civil Services Exam 2026</h1><p>Application starts: 2026-02-01</p></body></html>")
        
        self.logger.info("Starting Auto-Recovery Test...")
        data = self.safe_parse_notification(response)
        
        if data:
            self.logger.info(f"SUCCESS: Extracted data: {data}")
        else:
            self.logger.error("FAILURE: Parsing failed even with AI fallback.")

    def parse_notification(self, response, **kwargs):
        # INTENTIONALLY FAIL
        raise Exception("Simulated Selector Failure")

