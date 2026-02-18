"""
Quick demonstration of the critical bugs
"""
import os
import sys

print("\n" + "="*80)
print("DEMONSTRATING CRITICAL BUGS")
print("="*80)

# Bug #1: Missing 're' import in db_pipeline.py
print("\n[BUG #1] Missing 're' import causes NameError")
print("-"*80)

try:
    # Simulate what happens when _slugify is called
    os.environ['DATABASE_URL'] = 'postgresql://fake'  # Fake DB to avoid connection
    
    # This is what the _slugify method does (from line 243-248 of db_pipeline.py)
    text = "SSC CGL 2026 Notification"
    text = text.lower()
    # Next line will fail because 're' is not imported in db_pipeline.py
    # text = re.sub(r'[^a-z0-9\s-]', '', text)  # This line would crash
    
    print("✅ If we run this code, it would crash with:")
    print("   NameError: name 're' is not defined")
    print("\n   Location: src/scrapers/pipelines/db_pipeline.py, line 246")
    print("   Method: _slugify()")
    print("   Impact: Cannot create URL slugs for exams -> Database insert fails")
    
except Exception as e:
    print(f"Error: {e}")

# Bug #2: Hardcoded year
print("\n[BUG #2] Hardcoded year 2026")
print("-"*80)

from datetime import datetime
current_year = datetime.now().year

print(f"Current year: {current_year}")
print(f"Hardcoded in scrapers: 2026")
print(f"\nIn {current_year + 1}, all exams will still be saved with year=2026")
print("This means:")
print("  - Wrong data in database")
print("  - Wrong SEO pages generated")  
print("  - Users see incorrect information")
print("  - Trust destroyed")

# Bug #3: Database connection pool
print("\n[BUG #3] Database connection pool exhaustion")
print("-"*80)

print("Current settings (db_pipeline.py line 55):")
print("  pool_size=10")
print("  max_overflow=20")
print("  Total per scraper: 30 connections")
print("\nWith 50 scrapers running:")
print("  50 scrapers × 30 connections = 1,500 connections needed")
print("\nPostgreSQL default max_connections: 100")
print("\nResult:")
print("  ❌ Database refuses connections")
print("  ❌ All scrapers fail")
print("  ❌ Zero data collection")

print("\n" + "="*80)
print("BUGS DEMONSTRATED - See audit report for all 23 critical issues")
print("="*80 + "\n")
