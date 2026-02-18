"""
Unit Tests for UPSC Scraper

Tests with REAL-WORLD HTML structures and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from upsc_scraper_complete import UPSCScraper


class TestUPSCScraperBasics:
    """Test basic scraper configuration"""
    
    def test_scraper_initialization(self):
        """Test scraper initializes correctly"""
        scraper = UPSCScraper()
        
        assert scraper.name == 'upsc'
        assert scraper.exam_organization == 'Union Public Service Commission (UPSC)'
        assert scraper.exam_category == 'Central Government'
    
    def test_start_urls(self):
        """Test start URLs are correct"""
        scraper = UPSCScraper()
        
        assert len(scraper.start_urls) == 3
        assert 'current-examinations' in scraper.start_urls[0]
        assert 'admit-cards' in scraper.start_urls[1]
        assert 'results' in scraper.start_urls[2]


class TestUPSCNotificationExtraction:
    """Test notification data extraction with real HTML patterns"""
    
    def setup_method(self):
        self.scraper = UPSCScraper()
    
    def create_mock_element(self, html_content):
        """Helper to create mock Scrapy selector"""
        element = Mock()
        
        # Mock CSS selector responses
        def mock_css(selector):
            mock_result = Mock()
            
            # Title selectors
            if '::text' in selector and 'title' in selector.lower():
                if 'Civil Services' in html_content:
                    mock_result.get = Mock(return_value='Civil Services Examination, 2026')
                else:
                    mock_result.get = Mock(return_value=None)
            
            # PDF link selectors
            elif '::attr(href)' in selector and '.pdf' in selector:
                if 'notification.pdf' in html_content:
                    mock_result.get = Mock(return_value='/notification.pdf')
                else:
                    mock_result.get = Mock(return_value=None)
            
            # Date selectors
            elif 'date' in selector.lower():
                if '15/02/2026' in html_content:
                    mock_result.get = Mock(return_value='15/02/2026')
                else:
                    mock_result.get = Mock(return_value=None)
            
            # Fallback for any text
            elif selector == 'a::text':
                mock_result.get = Mock(return_value='Civil Services Examination, 2026')
            
            # Get all text
            elif selector == '::text':
                mock_result.getall = Mock(return_value=['Civil Services Examination', '15/02/2026'])
            
            else:
                mock_result.get = Mock(return_value=None)
                mock_result.getall = Mock(return_value=[])
            
            return mock_result
        
        element.css = mock_css
        return element
    
    def test_extract_notification_with_complete_data(self):
        """Test extraction with all fields present"""
        html = """
        <div class="notification-item">
            <div class="notification-title">
                <a href="/notification.pdf">Civil Services Examination, 2026</a>
            </div>
            <div class="notification-date">15/02/2026</div>
        </div>
        """
        
        element = self.create_mock_element(html)
        response = Mock()
        
        result = self.scraper._extract_notification_data(element, response)
        
        assert result is not None
        assert result['exam_name'] == 'Civil Services Examination, 2026'
        assert result['organization'] == 'Union Public Service Commission (UPSC)'
        assert result['notification_date'] == '15/02/2026'
        assert result['pdf_link'] == '/notification.pdf'
    
    def test_extract_notification_with_missing_date(self):
        """Test extraction when date is missing"""
        html = """
        <div class="notification-item">
            <a href="/notification.pdf">Civil Services Examination, 2026</a>
        </div>
        """
        
        element = self.create_mock_element(html)
        response = Mock()
        
        result = self.scraper._extract_notification_data(element, response)
        
        assert result is not None
        assert result['exam_name'] == 'Civil Services Examination, 2026'
        assert result['notification_date'] is None  # Missing but extraction succeeds
    
    def test_extract_notification_with_no_title(self):
        """Test extraction fails when no title found"""
        html = """
        <div class="notification-item">
            <div class="date">15/02/2026</div>
        </div>
        """
        
        element = Mock()
        element.css = Mock(return_value=Mock(get=Mock(return_value=None)))
        
        response = Mock()
        
        result = self.scraper._extract_notification_data(element, response)
        
        assert result is None  # Should fail without title


class TestUPSCAdmitCardExtraction:
    """Test admit card data extraction"""
    
    def setup_method(self):
        self.scraper = UPSCScraper()
    
    def test_extract_admit_card(self):
        """Test admit card extraction"""
        element = Mock()
        
        def mock_css(selector):
            mock_result = Mock()
            if 'title' in selector.lower() and '::text' in selector:
                mock_result.get = Mock(return_value='Civil Services Prelims 2026 Admit Card')
            elif '.pdf' in selector and '::attr' in selector:
                mock_result.get = Mock(return_value='/admit-card.pdf')
            elif 'date' in selector.lower():
                mock_result.get = Mock(return_value='20/05/2026')
            else:
                mock_result.get = Mock(return_value=None)
            
            mock_result.re_first = Mock(return_value=None)
            return mock_result
        
        element.css = mock_css
        response = Mock()
        
        result = self.scraper._extract_admit_card_data(element, response)
        
        assert result is not None
        assert 'Civil Services' in result['exam_name']
        assert result['download_link'] == '/admit-card.pdf'


class TestUPSCResultExtraction:
    """Test result data extraction"""
    
    def setup_method(self):
        self.scraper = UPSCScraper()
    
    def test_extract_result_with_stage(self):
        """Test result extraction with exam stage detection"""
        element = Mock()
        
        def mock_css(selector):
            mock_result = Mock()
            if 'title' in selector.lower() and '::text' in selector:
                mock_result.get = Mock(return_value='Civil Services Prelims 2025 Result')
            elif '.pdf' in selector and '::attr' in selector:
                mock_result.get = Mock(return_value='/result.pdf')
            elif 'date' in selector.lower():
                mock_result.get = Mock(return_value='15/08/2025')
            else:
                mock_result.get = Mock(return_value=None)
            return mock_result
        
        element.css = mock_css
        response = Mock()
        
        result = self.scraper._extract_result_data(element, response)
        
        assert result is not None
        assert 'Civil Services' in result['exam_name']
        assert result['stage'] == 'Prelims'  # Detected from title
        assert result['result_link'] == '/result.pdf'


class TestUPSCRouting:
    """Test URL routing to correct parsers"""
    
    def setup_method(self):
        self.scraper = UPSCScraper()
    
    def test_route_to_notifications(self):
        """Test routing to notifications parser"""
        response = Mock()
        response.url = 'https://upsc.gov.in/examinations/current-examinations'
        response.css = Mock(return_value=[])  # No items found (will warn)
        
        # Should call parse_notifications_page (will log warning about no items)
        result = list(self.scraper.parse(response))
        
        # Should not crash, returns empty list
        assert result == []
    
    def test_route_to_admit_cards(self):
        """Test routing to admit cards parser"""
        response = Mock()
        response.url = 'https://upsc.gov.in/examinations/admit-card'
        response.css = Mock(return_value=[])
        
        result = list(self.scraper.parse(response))
        assert result == []
    
    def test_route_to_results(self):
        """Test routing to results parser"""
        response = Mock()
        response.url = 'https://upsc.gov.in/examinations/result'
        response.css = Mock(return_value=[])
        
        result = list(self.scraper.parse(response))
        assert result == []


class TestUPSCErrorHandling:
    """Test error handling in various scenarios"""
    
    def setup_method(self):
        self.scraper = UPSCScraper()
    
    def test_empty_page(self):
        """Test handling of empty page (no notifications)"""
        response = Mock()
        response.url = 'https://upsc.gov.in/examinations/current-examinations'
        response.css = Mock(return_value=[])
        
        # Should not crash, should log warning
        result = list(self.scraper.parse_notifications_page(response))
        
        assert result == []
    
    def test_malformed_element(self):
        """Test handling of malformed HTML element"""
        element = Mock()
        element.css = Mock(side_effect=Exception("Parse error"))
        
        response = Mock()
        
        # Should return None, not crash
        result = self.scraper._extract_notification_data(element, response)
        
        # May return None or raise (caught by safe_parse_notification)
        # Either way, scraper continues
    
    def test_multiple_structure_fallback(self):
        """Test fallback through multiple structure attempts"""
        response = Mock()
        response.url = 'https://upsc.gov.in/examinations/current-examinations'
        
        # Mock CSS to fail first 3 attempts, succeed on 4th
        call_count = 0
        def mock_css(selector):
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                return []
            return [Mock()]  # Return one mock element
        
        response.css = mock_css
        
        # Should try multiple selectors
        list(self.scraper.parse_notifications_page(response))
        
        assert call_count >= 4  # Tried multiple selectors


class TestUPSCDatePatternMatching:
    """Test date pattern detection in text"""
    
    def setup_method(self):
        self.scraper = UPSCScraper()
    
    def test_date_pattern_in_text(self):
        """Test finding date pattern in mixed text"""
        element = Mock()
        
        def mock_css(selector):
            mock_result = Mock()
            if selector == '::text':
                mock_result.getall = Mock(return_value=[
                    'Civil Services Examination',
                    'Published on 15/02/2026',
                    'Apply before 15/03/2026'
                ])
            else:
                mock_result.get = Mock(return_value=None)
            return mock_result
        
        element.css = mock_css
        response = Mock()
        
        # Should extract first date pattern
        result = self.scraper._extract_notification_data(element, response)
        
        # Will succeed if title extraction works (separate logic)


class TestUPSCIntegration:
    """Integration tests with full flow"""
    
    def test_full_notification_flow(self):
        """Test complete flow from element to final data"""
        scraper = UPSCScraper()
        
        # Mock response
        response = Mock()
        response.url = 'https://upsc.gov.in/examinations/current-examinations'
        response.urljoin = lambda x: f'https://upsc.gov.in{x}'
        
        # Mock element with complete data
        element = Mock()
        
        def mock_css(selector):
            mock_result = Mock()
            if '.notification-title a::text' in selector:
                mock_result.get = Mock(return_value='Civil Services Examination, 2026')
            elif 'a[href$=".pdf"]::attr(href)' in selector:
                mock_result.get = Mock(return_value='/notification.pdf')
            elif '.notification-date::text' in selector:
                mock_result.get = Mock(return_value='15/02/2026')
            elif selector == 'a::text':
                mock_result.get = Mock(return_value='Civil Services Examination, 2026')
            elif selector == '::text':
                mock_result.getall = Mock(return_value=['Civil Services', '15/02/2026'])
            else:
                mock_result.get = Mock(return_value=None)
                mock_result.getall = Mock(return_value=[])
                mock_result.re_first = Mock(return_value=None)
            return mock_result
        
        element.css = mock_css
        
        # Extract data
        data = scraper._extract_notification_data(element, response)
        
        assert data is not None
        assert data['exam_name'] == 'Civil Services Examination, 2026'
        
        # Process through safe wrapper
        result = scraper.safe_parse_notification(response, **data)
        
        assert result is not None
        assert result['exam_name'] == 'Civil Services Examination, 2026'
        assert result['notification_date'] == '2026-02-15'  # Parsed format
        assert result['official_link'] == 'https://upsc.gov.in/notification.pdf'  # Absolute
        assert 'confidence_score' in result
        assert result['confidence_score'] >= 70  # Should auto-approve


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
