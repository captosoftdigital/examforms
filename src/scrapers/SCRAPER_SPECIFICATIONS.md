# Scraper Framework - Technical Specifications

## Mission-Critical Requirements

**Purpose**: Scrape 500+ government websites reliably, accurately, and respectfully  
**Scale**: 2,000+ exams, 100+ scrapers running 24/7  
**Reliability**: 95%+ success rate mandatory  
**Speed**: Complete scrape cycle in < 5 minutes per website  

---

## ASSUMPTIONS & CONDITIONS

### 1. Website Assumptions

#### ✅ What We CAN Assume
- Official government websites are authoritative sources
- Websites return HTML/PDF content
- Most sites use standard HTML tags
- HTTP status codes are reliable (200, 404, 500, etc.)
- Websites have some form of stable structure

#### ❌ What We CANNOT Assume
- ❌ HTML structure stays constant (sites redesign)
- ❌ Websites are always available (downtime happens)
- ❌ Requests are never blocked (rate limiting exists)
- ❌ Data is always complete (fields may be missing)
- ❌ Dates are in standard format (varies widely)
- ❌ All pages load fast (some take 10+ seconds)
- ❌ JavaScript is not required (some sites are SPA)

### 2. Network Assumptions

#### ✅ What Works
- HTTP/HTTPS requests with proper headers
- 5-10 second timeouts reasonable
- Retry logic handles temporary failures
- Proxy rotation avoids blocks

#### ❌ What Fails
- No timeout (hangs forever)
- Too aggressive (gets blocked)
- No User-Agent (rejected)
- No retry (one failure = data lost)

### 3. Data Assumptions

#### ✅ Valid Expectations
- Exam names are present (mandatory)
- Dates exist somewhere (may be in text, not structured)
- Links are provided (even if broken)
- PDFs may contain structured data

#### ❌ Invalid Expectations
- All fields always populated (often partial data)
- Dates in ISO format (usually in local format)
- Clean, structured HTML (often messy)
- No encoding issues (UTF-8 not guaranteed)

---

## FAILURE MODES & HANDLING

### 1. Network Failures

#### Scenario: Website Down / Unreachable

**Symptoms**:
```python
requests.exceptions.ConnectionError
requests.exceptions.Timeout
```

**Handling**:
```python
# Retry with exponential backoff
attempt = 1
while attempt <= max_retries:
    try:
        response = requests.get(url, timeout=30)
        break
    except (ConnectionError, Timeout) as e:
        if attempt == max_retries:
            log_error(f"Failed after {max_retries} attempts: {e}")
            return None
        wait_time = 2 ** attempt  # 2, 4, 8 seconds
        time.sleep(wait_time)
        attempt += 1
```

**Expected Outcome**: 
- Success on retry (temporary glitch)
- OR graceful failure logged for manual review

---

#### Scenario: Rate Limited / Blocked

**Symptoms**:
```python
HTTP 429 (Too Many Requests)
HTTP 403 (Forbidden)
Connection reset by peer
Empty responses
```

**Handling**:
```python
# Implement rate limiting BEFORE getting blocked
time.sleep(request_delay)  # Default: 5 seconds

# If blocked, back off exponentially
if response.status_code == 429:
    retry_after = response.headers.get('Retry-After', 60)
    time.sleep(int(retry_after))
    
# Rotate proxy if repeatedly blocked
if consecutive_blocks > 3:
    switch_proxy()
```

**Expected Outcome**: 
- Respectful scraping avoids blocks
- Proxy rotation if blocked
- Log for investigation

---

#### Scenario: Slow Response (10+ seconds)

**Symptoms**:
```python
requests.exceptions.ReadTimeout
Partial content received
```

**Handling**:
```python
# Set reasonable timeout
response = requests.get(
    url, 
    timeout=(10, 30)  # (connect, read) timeout
)

# If too slow, mark as degraded
if response.elapsed.total_seconds() > 20:
    log_warning(f"Slow response: {url}")
```

**Expected Outcome**: 
- Timeout prevents hanging
- Degraded source marked
- Manual review if persistent

---

### 2. Parsing Failures

#### Scenario: HTML Structure Changed

**Symptoms**:
```python
selector.get() returns None
Empty results from CSS/XPath
Previously working selectors fail
```

**Handling**:
```python
# Never assume element exists
title_element = response.css('.exam-title::text').get()
if not title_element:
    # Try alternative selectors
    title_element = response.css('h1::text').get()
    if not title_element:
        # Try XPath
        title_element = response.xpath('//h1/text()').get()
        
if not title_element:
    log_error(f"Could not extract title from {url}")
    # Mark for manual review
    create_manual_review_task({
        'url': url,
        'issue': 'Structure changed - title not found',
        'priority': 'HIGH'
    })
    return None

# Confidence scoring
confidence = calculate_confidence({
    'title_found': bool(title_element),
    'date_found': bool(date_element),
    'link_found': bool(link_element)
})

if confidence < 70:
    # Auto-reject, send to manual review
    flag_for_review()
```

**Expected Outcome**: 
- Alternative selectors tried
- Confidence score calculated
- Low confidence → manual review
- High confidence → auto-approved

---

#### Scenario: Malformed HTML

**Symptoms**:
```python
lxml.etree.ParserError
BeautifulSoup warnings
Encoding errors
```

**Handling**:
```python
from bs4 import BeautifulSoup
from lxml import html

# Try lxml first (fast)
try:
    tree = html.fromstring(response.text)
except Exception as e:
    log_warning(f"lxml failed, trying BeautifulSoup: {e}")
    # Fallback to BeautifulSoup (more forgiving)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract with BeautifulSoup
```

**Expected Outcome**: 
- BeautifulSoup handles malformed HTML
- Data extracted despite errors
- Warning logged for investigation

---

#### Scenario: Encoding Issues

**Symptoms**:
```python
UnicodeDecodeError
� characters in output
Garbled text
```

**Handling**:
```python
# Detect encoding
import chardet

def safe_decode(content):
    # Try UTF-8 first
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        # Detect actual encoding
        detected = chardet.detect(content)
        encoding = detected['encoding']
        try:
            return content.decode(encoding)
        except:
            # Last resort: ignore errors
            return content.decode('utf-8', errors='ignore')
```

**Expected Outcome**: 
- Correct encoding detected
- Text properly decoded
- Fallback prevents crash

---

### 3. Data Quality Issues

#### Scenario: Missing Mandatory Fields

**Symptoms**:
```python
exam_name = None
notification_date = None
```

**Handling**:
```python
# Define mandatory fields
MANDATORY_FIELDS = ['exam_name', 'organization']

def validate_data(data):
    missing = []
    for field in MANDATORY_FIELDS:
        if not data.get(field):
            missing.append(field)
    
    if missing:
        log_error(f"Missing mandatory fields: {missing}")
        return False, missing
    
    return True, None

# Use validation
is_valid, missing = validate_data(scraped_data)
if not is_valid:
    log_error(f"Incomplete data: {missing}")
    # Save partial data with flag
    save_partial_data(scraped_data, missing_fields=missing)
    return None
```

**Expected Outcome**: 
- Invalid data rejected
- Partial data saved with flag
- Manual review triggered

---

#### Scenario: Invalid Dates

**Symptoms**:
```python
"First week of March" (ambiguous)
"15-03-2026" vs "03-15-2026" (format unclear)
"15th March" (no year)
```

**Handling**:
```python
from dateutil import parser
import re

def parse_date(date_string):
    if not date_string:
        return None
    
    # Clean the string
    date_string = date_string.strip()
    
    # Try standard parsing
    try:
        dt = parser.parse(date_string, fuzzy=True)
        # If year is missing, assume current year
        if dt.year == datetime.now().year - 100:  # parser default
            dt = dt.replace(year=datetime.now().year)
        return dt.date()
    except:
        pass
    
    # Try regex patterns for common formats
    patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_string)
        if match:
            # Try parsing the matched portion
            try:
                return parser.parse(match.group(0)).date()
            except:
                continue
    
    # If all fails, log for manual review
    log_warning(f"Could not parse date: {date_string}")
    return None
```

**Expected Outcome**: 
- Most dates parsed correctly
- Ambiguous dates → None (not wrong date)
- Manual review for unparseable dates

---

#### Scenario: Duplicate Data

**Symptoms**:
```python
Same exam scraped twice
Multiple notifications for same exam/year
```

**Handling**:
```python
def check_duplicate(exam_slug, year, event_type):
    existing = db.query(
        ExamEvent
    ).filter(
        exam_id == exam_slug,
        year == year,
        event_type == event_type
    ).first()
    
    if existing:
        log_info(f"Duplicate found: {exam_slug} {year} {event_type}")
        # Update instead of insert
        update_existing(existing, new_data)
        return True
    
    return False

# Use before inserting
if not check_duplicate(slug, year, 'notification'):
    insert_new_record(data)
else:
    log_info("Updated existing record instead of creating duplicate")
```

**Expected Outcome**: 
- Duplicates detected
- Existing records updated
- No duplicate data in database

---

### 4. System Failures

#### Scenario: Database Connection Lost

**Symptoms**:
```python
psycopg2.OperationalError
Connection refused
```

**Handling**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def save_to_database(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log_error(f"Database error: {e}")
        raise

# If all retries fail
try:
    save_to_database(scraped_data)
except:
    # Save to file as backup
    save_to_json_file(scraped_data, 'backup/')
    alert_admin("Database connection failed, data saved to backup")
```

**Expected Outcome**: 
- Retry logic handles temporary issues
- Backup file created if all fails
- No data loss

---

#### Scenario: Out of Memory

**Symptoms**:
```python
MemoryError
System slow/frozen
```

**Handling**:
```python
# Process in batches, not all at once
def scrape_large_list(urls):
    batch_size = 100
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        process_batch(batch)
        # Clear memory
        gc.collect()

# Stream large responses instead of loading in memory
def download_large_pdf(url):
    response = requests.get(url, stream=True)
    with open('output.pdf', 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
```

**Expected Outcome**: 
- Memory usage controlled
- Large files handled
- System stable

---

#### Scenario: Disk Space Full

**Symptoms**:
```python
OSError: [Errno 28] No space left on device
```

**Handling**:
```python
import shutil

def check_disk_space():
    stat = shutil.disk_usage('/')
    free_gb = stat.free / (1024**3)
    
    if free_gb < 5:  # Less than 5GB free
        alert_admin("Low disk space: {free_gb:.2f}GB remaining")
        # Cleanup old logs
        cleanup_old_files()
        return False
    
    return True

# Check before large operations
if not check_disk_space():
    log_error("Insufficient disk space, aborting")
    return None
```

**Expected Outcome**: 
- Disk space monitored
- Cleanup triggered automatically
- Failures prevented

---

## SCRAPER DESIGN PATTERNS

### 1. Base Scraper Class

**Purpose**: Provide common functionality for all scrapers

**Features**:
- Retry logic
- Rate limiting
- Error handling
- Data validation
- Logging
- Database integration

**Usage**:
```python
class UPSCScraper(BaseExamScraper):
    name = 'upsc'
    
    def parse(self, response):
        # Custom parsing logic
        # Base class handles errors, retries, logging
```

---

### 2. Scraper Pipeline

**Flow**:
```
1. Fetch URL
   ↓
2. Check Rate Limit
   ↓
3. Parse HTML
   ↓
4. Validate Data
   ↓
5. Check Duplicates
   ↓
6. Save to Database
   ↓
7. Log Success
```

**Each step has error handling**

---

### 3. Confidence Scoring

**Purpose**: Determine data reliability

**Calculation**:
```python
def calculate_confidence(data):
    score = 0
    
    # Mandatory fields found
    if data.get('exam_name'): score += 30
    if data.get('organization'): score += 20
    
    # Optional but important fields
    if data.get('notification_date'): score += 20
    if data.get('official_link'): score += 15
    if data.get('application_start'): score += 10
    if data.get('application_end'): score += 5
    
    # Source credibility
    if is_official_domain(data['source_url']): score += 10
    
    return min(score, 100)

# Usage
confidence = calculate_confidence(scraped_data)
if confidence >= 70:
    auto_approve()
else:
    manual_review()
```

---

### 4. Selector Fallback Strategy

**Purpose**: Handle HTML changes

**Pattern**:
```python
def extract_title(response):
    # Try primary selector
    title = response.css('.notification-title::text').get()
    if title:
        return clean_text(title)
    
    # Try alternative 1
    title = response.css('h2.title::text').get()
    if title:
        return clean_text(title)
    
    # Try alternative 2
    title = response.xpath('//div[@class="content"]//h2/text()').get()
    if title:
        return clean_text(title)
    
    # Try generic (last resort)
    title = response.css('h1::text, h2::text').get()
    if title:
        return clean_text(title)
    
    # All failed
    return None
```

---

## PERFORMANCE REQUIREMENTS

### Response Time

| Operation | Target | Maximum |
|-----------|--------|---------|
| Single page scrape | < 5 seconds | 30 seconds |
| Full website scrape | < 5 minutes | 15 minutes |
| Database save | < 100ms | 1 second |
| Validation | < 10ms | 100ms |

### Throughput

| Metric | Target |
|--------|--------|
| Pages per hour | 1,000+ |
| Concurrent scrapers | 10+ |
| Success rate | 95%+ |
| False positives | < 1% |

### Resource Usage

| Resource | Limit |
|----------|-------|
| Memory per scraper | < 200MB |
| CPU per scraper | < 20% |
| Network bandwidth | < 1Mbps |
| Disk I/O | Minimal (stream to DB) |

---

## TESTING STRATEGY

### Unit Tests

Test individual functions:
- Date parsing (20+ date formats)
- Text cleaning (Unicode, HTML entities)
- URL validation
- Data validation

### Integration Tests

Test full scraping flow:
- Mock website responses
- Test error handling
- Test retry logic
- Test database integration

### Stress Tests

Test at scale:
- 1000 pages in parallel
- Network failures (50% failure rate)
- Slow responses (10+ seconds)
- Memory limits

---

## MONITORING & ALERTS

### Metrics to Track

```python
metrics = {
    'scraper_name': 'upsc',
    'total_runs': 100,
    'successful_runs': 95,
    'failed_runs': 5,
    'success_rate': 0.95,
    'avg_duration_seconds': 12.5,
    'items_scraped': 450,
    'items_inserted': 420,
    'items_updated': 30,
    'errors': [
        {'type': 'timeout', 'count': 3},
        {'type': 'parse_error', 'count': 2}
    ]
}
```

### Alert Thresholds

| Condition | Alert Level | Action |
|-----------|-------------|--------|
| Success rate < 80% | WARNING | Investigate |
| Success rate < 50% | CRITICAL | Stop scraper |
| No runs in 24 hours | ERROR | Check scheduler |
| Avg duration > 30s | WARNING | Optimize |
| Database errors | CRITICAL | Check connection |

---

## READY TO IMPLEMENT

All assumptions documented ✅  
All failure modes identified ✅  
All edge cases covered ✅  
Performance targets defined ✅  
Testing strategy ready ✅  

**Next: Implement Base Scraper Framework**

