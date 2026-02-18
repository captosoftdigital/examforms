"""
Unit Tests for SSC Scraper

ASSUMPTIONS (stated before code):
1. SSC pages can be represented with minimal HTML snippets.
2. CSS selectors used in scraper are stable enough for unit testing.
3. Date strings are in common formats (DD/MM/YYYY, DD-MM-YYYY).
4. Missing fields should not crash parsing (graceful handling).
"""

import pytest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ssc_scraper_complete import SSCScraper


class TestSSCScraperBasics:
    def test_scraper_initialization(self):
        scraper = SSCScraper()
        assert scraper.name == 'ssc'
        assert scraper.exam_organization == 'Staff Selection Commission (SSC)'
        assert scraper.exam_category == 'Central Government'

    def test_start_urls(self):
        scraper = SSCScraper()
        assert len(scraper.start_urls) == 3
        assert 'LatestNotification' in scraper.start_urls[0]
        assert 'AdmitCard' in scraper.start_urls[1]
        assert 'Results' in scraper.start_urls[2]


class TestSSCNotificationExtraction:
    def setup_method(self):
        self.scraper = SSCScraper()

    def _mock_element(self, title=None, date=None, link=None):
        element = Mock()

        def mock_css(selector):
            mock_result = Mock()
            if 'first-child' in selector or 'title' in selector or 'h2' in selector or 'h3' in selector:
                mock_result.get = Mock(return_value=title)
            elif 'nth-child(2)' in selector or 'date' in selector:
                mock_result.get = Mock(return_value=date)
            elif 'href' in selector:
                mock_result.get = Mock(return_value=link)
            else:
                mock_result.get = Mock(return_value=None)
            return mock_result

        element.css = mock_css
        return element

    def test_extract_notification_complete(self):
        element = self._mock_element(
            title='SSC CGL 2026 Notification',
            date='15/03/2026',
            link='/cgl-notification.pdf'
        )
        response = Mock()
        result = self.scraper._extract_notification_data(element, response)

        assert result is not None
        assert result['exam_name'] == 'SSC CGL 2026 Notification'
        assert result['notification_date'] == '15/03/2026'
        assert result['pdf_link'] == '/cgl-notification.pdf'

    def test_extract_notification_missing_title(self):
        element = self._mock_element(title=None, date='15/03/2026', link='/cgl.pdf')
        response = Mock()
        result = self.scraper._extract_notification_data(element, response)

        assert result is None


class TestSSCAdmitCardExtraction:
    def setup_method(self):
        self.scraper = SSCScraper()

    def test_extract_admit_card(self):
        element = Mock()

        def mock_css(selector):
            mock_result = Mock()
            if 'first-child' in selector or 'title' in selector:
                mock_result.get = Mock(return_value='SSC CGL Admit Card 2026')
            elif 'date' in selector:
                mock_result.get = Mock(return_value='20/06/2026')
            elif 'href' in selector:
                mock_result.get = Mock(return_value='/admit-card.pdf')
            else:
                mock_result.get = Mock(return_value=None)
            return mock_result

        element.css = mock_css
        response = Mock()
        result = self.scraper._extract_admit_card_data(element, response)

        assert result is not None
        assert 'SSC CGL' in result['exam_name']
        assert result['download_link'] == '/admit-card.pdf'


class TestSSCResultExtraction:
    def setup_method(self):
        self.scraper = SSCScraper()

    def test_extract_result(self):
        element = Mock()

        def mock_css(selector):
            mock_result = Mock()
            if 'first-child' in selector or 'title' in selector:
                mock_result.get = Mock(return_value='SSC CGL Tier 1 Result 2026')
            elif 'date' in selector:
                mock_result.get = Mock(return_value='15/09/2026')
            elif 'href' in selector:
                mock_result.get = Mock(return_value='/result.pdf')
            else:
                mock_result.get = Mock(return_value=None)
            return mock_result

        element.css = mock_css
        response = Mock()
        result = self.scraper._extract_result_data(element, response)

        assert result is not None
        assert result['stage'] == 'Tier'
        assert result['result_link'] == '/result.pdf'


class TestSSCRouting:
    def setup_method(self):
        self.scraper = SSCScraper()

    def test_route_notifications(self):
        response = Mock()
        response.url = 'https://ssc.nic.in/Portal/LatestNotification'
        response.css = Mock(return_value=[])
        result = list(self.scraper.parse(response))
        assert result == []

    def test_route_admit_cards(self):
        response = Mock()
        response.url = 'https://ssc.nic.in/Portal/AdmitCard'
        response.css = Mock(return_value=[])
        result = list(self.scraper.parse(response))
        assert result == []

    def test_route_results(self):
        response = Mock()
        response.url = 'https://ssc.nic.in/Portal/Results'
        response.css = Mock(return_value=[])
        result = list(self.scraper.parse(response))
        assert result == []


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
