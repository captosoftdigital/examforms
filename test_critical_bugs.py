"""
Test script to demonstrate critical bugs found in audit
"""

print("=" * 80)
print("TESTING CRITICAL BUGS FROM AUDIT")
print("=" * 80)

# Test 1: Missing 're' import in db_pipeline.py
print("\n[TEST 1] Missing 're' import in db_pipeline.py")
print("-" * 80)

try:
    # Read the file and check if 're' is imported
    with open('src/scrapers/pipelines/db_pipeline.py', 'r') as f:
        content = f.read()
        
    has_import_re = 'import re' in content
    uses_re = 're.sub' in content
    
    print(f"File imports 're': {has_import_re}")
    print(f"File uses 're.sub': {uses_re}")
    
    if uses_re and not has_import_re:
        print("❌ CRITICAL BUG CONFIRMED: File uses 're' module but doesn't import it!")
        print("   This will cause NameError when _slugify() is called")
    else:
        print("✅ No issue found")
        
except Exception as e:
    print(f"Error: {e}")

# Test 2: Hardcoded year 2026
print("\n[TEST 2] Hardcoded year 2026 in scrapers")
print("-" * 80)

files_to_check = [
    'src/scrapers/ssc_scraper.py',
    'src/scrapers/upsc_scraper.py'
]

for filepath in files_to_check:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        hardcoded_years = []
        for i, line in enumerate(lines, 1):
            if "'year': 2026" in line or '"year": 2026' in line:
                hardcoded_years.append((i, line.strip()))
        
        if hardcoded_years:
            print(f"\n{filepath}:")
            print(f"  ❌ Found {len(hardcoded_years)} hardcoded 'year: 2026' instances:")
            for line_num, line in hardcoded_years:
                print(f"     Line {line_num}: {line}")
        else:
            print(f"\n{filepath}: ✅ No hardcoded years found")
            
    except Exception as e:
        print(f"Error checking {filepath}: {e}")

# Test 3: Check test file imports
print("\n[TEST 3] Test file imports")
print("-" * 80)

test_files = [
    ('src/scrapers/tests/test_base_scraper.py', 'base_scraper_complete'),
    ('src/scrapers/tests/test_ssc_scraper.py', 'ssc_scraper_complete'),
    ('src/scrapers/tests/test_upsc_scraper.py', 'upsc_scraper_complete'),
]

for test_file, expected_import in test_files:
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        
        if f'from {expected_import} import' in content:
            print(f"\n{test_file}:")
            print(f"  ✅ Imports from '{expected_import}' (file exists)")
        else:
            print(f"\n{test_file}:")
            print(f"  ⚠️  Does not import from '{expected_import}'")
            
    except Exception as e:
        print(f"Error checking {test_file}: {e}")

print("\n" + "=" * 80)
print("AUDIT VERIFICATION COMPLETE")
print("=" * 80)
