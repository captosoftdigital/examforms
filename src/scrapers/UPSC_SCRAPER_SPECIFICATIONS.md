# UPSC Scraper - Technical Specifications

## Target Website

**Organization**: Union Public Service Commission (UPSC)  
**Website**: https://upsc.gov.in  
**Primary Pages**:
- Current Examinations: https://upsc.gov.in/examinations/current-examinations
- Admit Cards: https://upsc.gov.in/examinations/admit-cards
- Results: https://upsc.gov.in/examinations/results

**Priority**: CRITICAL (top government exam board)  
**Update Frequency**: Every 2 hours  

---

## ASSUMPTIONS ABOUT UPSC WEBSITE

### ✅ What We CAN Assume

1. **Authoritative Source**: UPSC.gov.in is the official government website
2. **Standard HTTP**: Website uses standard HTTP/HTTPS protocols
3. **Public Access**: No login/authentication required for exam information
4. **PDF Notifications**: Most official notifications are in PDF format
5. **Stable Domain**: upsc.gov.in domain is stable and trusted
6. **English Content**: Primary content in English
7. **Date Formats**: Dates typically in Indian format (DD/MM/YYYY or DD-MM-YYYY)

### ❌ What We CANNOT Assume

1. ❌ **HTML Structure Stays Constant**: UPSC redesigns website periodically
2. ❌ **Element IDs/Classes Are Stable**: CSS classes may change
3. ❌ **Page Load Speed**: Government sites can be slow (5-10+ seconds)
4. ❌ **Always Available**: Site has downtime, especially during result days
5. ❌ **Complete Information**: Some exam details may be missing
6. ❌ **Consistent Formatting**: Date formats, text formatting varies
7. ❌ **No JavaScript**: Some pages may use JavaScript for content loading
8. ❌ **Single Page Type**: Different exam types have different page layouts

---

## WEBSITE STRUCTURE ANALYSIS (as of Jan 2026)

### Current Examinations Page

**URL Pattern**: `https://upsc.gov.in/examinations/current-examinations`

**Expected Structure** (may change):
```html
<div class="exam-notification">
    <div class="notification-title">
        <a href="/notification.pdf">Civil Services Examination, 2026</a>
    </div>
    <div class="notification-date">
        <span>Date: 15/02/2026</span>
    </div>
    <div class="description">
        <!-- Additional details -->
    </div>
</div>
```

**Alternative Structures** (observed in past):
- Table-based layout with `<table><tr><td>`
- List-based with `<ul><li>`
- Simple paragraph-based with `<p><a>`

**Selectors to Try** (in order of preference):
1. `.exam-notification` or `.notification-item`
2. `.exam-list li` or `ul.examinations li`
3. `table.notifications tr`
4. `div[class*="notification"]` (contains "notification")
5. Generic: `div:has(a[href*=".pdf"])`

### Admit Card Page

**URL Pattern**: `https://upsc.gov.in/examinations/admit-cards`

**Expected Elements**:
- Exam name
- Release date
- Download link (usually PDF or separate page)
- Exam date (when the exam will be held)

**Common Issues**:
- Admit card link may go to intermediate page (not direct PDF)
- Multiple exam stages (Prelims, Mains) listed separately
- Some admit cards for different regions

### Results Page

**URL Pattern**: `https://upsc.gov.in/examinations/results`

**Expected Elements**:
- Exam name with year
- Result declaration date
- Result PDF link or check page link
- Sometimes includes cutoff information

**Common Issues**:
- Final result vs. written result (multiple stages)
- Roll number-based vs. full result list
- Cutoff marks may be in separate PDF

---

## FAILURE MODES & HANDLING

### 1. Website Down / Slow

**Symptoms**:
```
ConnectionError, Timeout, 503 Service Unavailable
```

**Handling**:
```python
# Scrapy's retry middleware handles this
# custom_settings already configured:
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 30
```

**Expected Outcome**:
- Retry 3 times with exponential backoff
- If all fail: Log error, skip this run
- Alert admin if consecutive failures > 5

---

### 2. HTML Structure Changed

**Symptoms**:
```python
selector.get() returns None
All primary selectors fail
```

**Handling**:
```python
# Use multiple fallback selectors
title = self.try_selectors(response, [
    '.notification-title a::text',
    '.exam-title::text',
    'h3 a::text',
    'table td:first-child a::text',
    'a[href*=".pdf"]::text'
])

if not title:
    # Last resort: extract any text near PDF link
    title = extract_near_pdf_link(response)

if not title:
    log_error("Structure changed, manual review needed")
    create_structure_change_alert()
    return None
```

**Expected Outcome**:
- Fallback selectors catch most changes
- Low confidence score triggers manual review
- Admin alerted to verify scraper

---

### 3. Incomplete Data

**Symptoms**:
```python
Exam name present but dates missing
PDF link broken
Date in unexpected format
```

**Handling**:
```python
# Base class handles this automatically
# - Partial data saved with validation_failed flag
# - Missing fields logged
# - Confidence score reflects completeness

# Example result:
{
    'exam_name': 'Civil Services Examination',
    'organization': 'UPSC',
    'notification_date': None,  # Missing
    'pdf_link': 'https://...',
    'confidence_score': 50,  # Below 70
    'requires_manual_review': True,
    'missing_fields': ['notification_date']
}
```

**Expected Outcome**:
- Partial data saved (not lost)
- Flagged for manual review
- Admin fills in missing data

---

### 4. Multiple Exam Formats

**Symptoms**:
```
Different page structures for different exams:
- Civil Services: Detailed notification
- NDA: Simple announcement
- Engineering Services: Table format
```

**Handling**:
```python
def parse_notification(self, response, **metadata):
    # Try to detect page type
    if response.css('.detailed-notification'):
        return self._parse_detailed_format(response)
    elif response.css('table.exam-table'):
        return self._parse_table_format(response)
    else:
        return self._parse_generic_format(response)

def _parse_generic_format(self, response):
    # Most flexible parser - tries all selectors
    # Works for 80%+ of pages
```

**Expected Outcome**:
- Correct parser selected automatically
- If all parsers fail: manual review
- New formats identified for future updates

---

### 5. PDF-Only Notifications

**Symptoms**:
```
Page only has PDF link, no extracted text
All details inside PDF
```

**Handling**:
```python
# Phase 1: Extract basic info from page
data = {
    'exam_name': title_from_link_text,
    'pdf_link': pdf_url,
    'notification_date': date_from_page,
}

# Phase 2 (future): Parse PDF content
# For now: Manual review adds PDF details
# TODO: Implement PDF parsing (PyPDF2/pdfplumber)
```

**Expected Outcome**:
- Basic data captured immediately
- PDF parsing added in future sprint
- Manual review extracts PDF details temporarily

---

### 6. Duplicate Notifications

**Symptoms**:
```
Same exam notification appears multiple times
Updated notification for same exam
```

**Handling**:
```python
def before_save(self, data):
    # Check if exam + year + event_type exists
    existing = database.query(
        exam_name=data['exam_name'],
        year=data['year'],
        event_type='notification'
    )
    
    if existing:
        if is_update(existing, data):
            update_record(existing, data)
            log_info("Updated existing notification")
        else:
            log_info("Duplicate, skipping")
        return None  # Don't insert
    
    return data  # New notification
```

**Expected Outcome**:
- No duplicate records
- Updates captured correctly
- Changelog maintained

---

## PAGE TYPES TO HANDLE

### 1. Notification Pages (Priority 1)

**Information to Extract**:
- ✅ Exam name
- ✅ Notification date
- ✅ Application start date
- ✅ Application end date
- ✅ Exam date (if mentioned)
- ✅ Total vacancies
- ✅ PDF link
- ✅ Fee details (if available)

**Success Criteria**: 85%+ fields extracted

---

### 2. Admit Card Pages (Priority 1)

**Information to Extract**:
- ✅ Exam name
- ✅ Admit card release date
- ✅ Exam date
- ✅ Download link
- ✅ Instructions (optional)

**Success Criteria**: 80%+ fields extracted

---

### 3. Result Pages (Priority 1)

**Information to Extract**:
- ✅ Exam name with stage (Prelims/Mains)
- ✅ Result date
- ✅ Result PDF link
- ✅ Cutoff marks (if available)
- ✅ Total appeared/qualified (if available)

**Success Criteria**: 75%+ fields extracted

---

### 4. Answer Key Pages (Priority 2)

**Information to Extract**:
- ✅ Exam name
- ✅ Answer key release date
- ✅ Objection period dates
- ✅ Download link

**Success Criteria**: 70%+ fields extracted

---

### 5. Interview/DV Pages (Priority 3)

**Information to Extract**:
- ✅ Exam name
- ✅ Interview schedule
- ✅ Document verification dates
- ✅ Venue details (optional)

**Success Criteria**: 60%+ fields extracted

---

## SELECTORS MAP

### Primary Selectors (Try First)

```python
SELECTORS = {
    'exam_title': [
        '.notification-title a::text',
        '.exam-title::text',
        'h3.title::text',
        'h2 a::text',
    ],
    
    'date': [
        '.notification-date::text',
        '.date::text',
        'span:contains("Date:")::text',
        'td:contains("Date") + td::text',
    ],
    
    'pdf_link': [
        'a[href$=".pdf"]::attr(href)',
        'a:contains("Download") ::attr(href)',
        '.download-link::attr(href)',
    ],
    
    'description': [
        '.notification-description::text',
        '.description::text',
        'p::text',
    ],
    
    'vacancies': [
        ':contains("Total Vacancies")::text',
        ':contains("No. of Vacancies")::text',
        'td:contains("Vacancies") + td::text',
    ],
}
```

### Fallback Strategy

If all primary selectors fail:
1. Try XPath equivalents
2. Try generic selectors (all `<a>` tags with "notification" in href)
3. Try text matching with regex
4. Return None and flag for manual review

---

## TESTING STRATEGY

### Unit Tests

Test individual parsing methods with:
- Real HTML snapshots (saved from actual site)
- Mocked responses with different structures
- Edge cases (missing elements, malformed HTML)

### Integration Tests

Test full scraping flow:
- Start from main page
- Follow links
- Extract data
- Save to database (test DB)
- Verify data accuracy

### Regression Tests

When structure changes:
1. Save new HTML snapshot
2. Add test case for new structure
3. Ensure old structure still works (if possible)
4. Update selectors if needed

---

## EXPECTED RESULTS

### Success Metrics

| Metric | Target | Acceptable |
|--------|--------|------------|
| Pages scraped | 100% | 95% |
| Data extracted | 90% complete | 75% complete |
| Accuracy | 99% | 95% |
| False positives | <1% | <3% |
| Scrape duration | <5 min | <10 min |

### Typical Run Output

```
UPSC Scraper Run - 2026-01-29 10:00:00
==========================================
Pages scraped: 15
Items extracted: 12
Items valid: 10 (83%)
Items invalid: 2 (17%)
Errors: 1
Duration: 3m 24s

Breakdown:
- Notifications: 5 extracted
- Admit Cards: 3 extracted  
- Results: 4 extracted

Flagged for review: 2
- Civil Services (missing date)
- NDA (low confidence: 65%)

Errors:
- Timeout on results page (will retry next run)
```

---

## MONITORING & ALERTS

### Alert Triggers

**CRITICAL (Immediate)**:
- No data extracted (all selectors failed)
- Consecutive failures > 5
- Success rate < 50%

**HIGH (Within 1 hour)**:
- Success rate < 80%
- Manual review queue > 10
- Structure change detected

**MEDIUM (Daily digest)**:
- New exams detected
- Exam status changes
- Low confidence items

### Dashboard Metrics

Track over time:
- Success rate trend
- Average confidence score
- Items flagged for review
- Scrape duration
- Error frequency by type

---

## READY TO IMPLEMENT

All assumptions documented ✅  
All failure modes identified ✅  
All selectors mapped ✅  
Testing strategy defined ✅  
Success criteria clear ✅  

**Next: Implement UPSC Scraper code**

