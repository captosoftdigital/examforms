import os
import sys

# Scrapy Settings
BOT_NAME = 'examforms_scrapers'

SPIDER_MODULES = ['src.scrapers']
NEWSPIDER_MODULE = 'src.scrapers'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
ROBOTSTXT_OBEY = False
LOG_LEVEL = 'INFO'
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Pipelines (Django ORM Pipeline & S3 Pipeline)
ITEM_PIPELINES = {
    'src.scrapers.pipelines.media_pipeline.S3MediaPipeline': 100, # Run first to download files
    'src.scrapers.pipelines.db_pipeline.DatabasePipeline': 300,
}

# AWS S3 Settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL') # For MinIO support
AWS_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_Use_SSL = True
AWS_VERIFY = True

FILES_STORE = os.getenv('S3_BUCKET_NAME', 's3://examforms-media/')

# AI Parsing Settings
ENABLE_AI_PARSING = os.getenv('ENABLE_AI_PARSING', 'False').lower() == 'true'
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai') # openai or gemini

# Django Integration
# Add project root and admin_panel to sys.path
# Using relative paths assuming settings.py is in src/scrapers/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # src/scrapers
SRC_DIR = os.path.dirname(CURRENT_DIR)                    # src
PROJECT_ROOT = os.path.dirname(SRC_DIR)                   # d:/examforms.org

sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))
sys.path.append(os.path.join(PROJECT_ROOT, 'src', 'admin_panel'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')

import django
try:
    django.setup()
except Exception as e:
    print(f"Failed to setup Django: {e}")
