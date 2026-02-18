
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from scrapers.pipelines.db_pipeline import DatabasePipeline
from scrapers.ssc_scraper import SSCScraper
from scrapers.upsc_scraper import UPSCScraper

class TestCriticalBugFixes(unittest.TestCase):
    
    def test_re_import_and_slugify(self):
        """Test that re is imported and _slugify works without error"""
        print("\nTesting Bug #1: Missing 're' import...")
        pipeline = DatabasePipeline.__new__(DatabasePipeline) # Skip __init__ to avoid db connection
        try:
            slug = pipeline._slugify("SSC CGL 2026 Notification")
            print(f"  ✅ _slugify() worked! Result: {slug}")
            self.assertEqual(slug, "ssc-cgl-2026-notification")
        except NameError as e:
            self.fail(f"❌ NameError in _slugify: {e}")
        except Exception as e:
            self.fail(f"❌ Unexpected error in _slugify: {e}")

    @patch('scrapers.pipelines.db_pipeline.create_engine')
    @patch('scrapers.pipelines.db_pipeline.sessionmaker')
    @patch('os.getenv')
    def test_connection_pool_singleton(self, mock_getenv, mock_sessionmaker, mock_create_engine):
        """Test that DatabasePipeline uses a singleton for the engine"""
        print("\nTesting Bug #3: Connection pool singleton...")
        
        # Mock DATABASE_URL
        mock_getenv.return_value = "postgresql://user:pass@localhost/db"
        
        # Reset singleton for testing
        DatabasePipeline._engine = None
        DatabasePipeline._Session = None
        
        # Mock engine and connection
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Instantiate first pipeline
        p1 = DatabasePipeline()
        engine1 = DatabasePipeline._engine
        
        # Instantiate second pipeline
        p2 = DatabasePipeline()
        engine2 = DatabasePipeline._engine
        
        print(f"  Pipeline 1 engine: {id(engine1)}")
        print(f"  Pipeline 2 engine: {id(engine2)}")
        
        if engine1 is engine2:
            print("  ✅ Engine is a singleton (reused properly)")
        else:
            print("  ❌ Engine is NOT a singleton (new connection pool created!)")
            
        self.assertIs(engine1, engine2, "Engine should be a singleton")
        self.assertEqual(mock_create_engine.call_count, 1, "create_engine should be called exactly once")

    def test_hardcoded_year_removed(self):
        """Test that scrapers don't have hardcoded 2026"""
        print("\nTesting Bug #2: Hardcoded year 2026...")
        
        # We check the source code for the specific bad pattern
        scrapers = [
            ('src/scrapers/ssc_scraper.py', 'SSCScraper'),
            ('src/scrapers/upsc_scraper.py', 'UPSCScraper')
        ]
        
        for file_path, scraper_name in scrapers:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "'year': 2026" in content or '"year": 2026' in content:
                print(f"  ❌ {scraper_name}: Hardcoded 2026 FOUND in {file_path}")
                self.fail(f"Hardcoded 2026 found in {scraper_name}")
            else:
                print(f"  ✅ {scraper_name}: Hardcoded 2026 NOT found")

if __name__ == '__main__':
    with open('verification_results.txt', 'w', encoding='utf-8') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        unittest.main(testRunner=runner, exit=False)
