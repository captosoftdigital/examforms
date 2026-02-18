import os
import sys
import django
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'admin_panel'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

# Import spider
from src.scrapers.upsc_scraper import UPSCScraper
from dotenv import load_dotenv

load_dotenv()

def run_spider():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'LOG_LEVEL': 'INFO',
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'ITEM_PIPELINES': {
            'src.scrapers.pipelines.db_pipeline.DatabasePipeline': 300,
        }
    })

    process.crawl(UPSCScraper)
    process.start()

if __name__ == '__main__':
    run_spider()
