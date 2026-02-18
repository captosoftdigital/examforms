# SSC Scraper - Technical Specifications

## Assumptions (Stated Before Code)

### ✅ We Assume
1. Official SSC portal (https://ssc.nic.in) is authoritative.
2. Core pages exist and are public:
   - Latest Notifications
   - Admit Card
   - Results
3. SSC regional sites may use similar but not identical layouts.
4. PDF links are the primary source of truth.

### ❌ We Do NOT Assume
1. HTML structure remains stable (selectors may break).
2. Dates are always present or consistently formatted.
3. All pages are fast (timeouts possible).
4. Regional sites use the same CSS classes.

---

## Primary URLs
- Notifications: https://ssc.nic.in/Portal/LatestNotification
- Admit Cards: https://ssc.nic.in/Portal/AdmitCard
- Results: https://ssc.nic.in/Portal/Results

Regional Sites (partial):
- https://ssc-cr.org
- https://ssc-wr.org
- https://sscner.org.in
- https://sscsr.gov.in

---

## Page Types

### 1. Notifications
Extract:
- Exam name
- Notification date
- PDF link
- Application dates (if present)
- Fee (if present)

### 2. Admit Cards
Extract:
- Exam name
- Release date
- Download link
- Exam date (if present)

### 3. Results
Extract:
- Exam name + stage
- Result date
- Result PDF link

---

## Failure Handling
- Structure changes → fallback selectors + manual review flag
- Missing data → partial save + confidence scoring
- Timeout → retry via Scrapy, skip on repeated failures

---

## Success Criteria
- Notifications: 85%+ fields extracted
- Admit cards: 80%+ fields extracted
- Results: 75%+ fields extracted
- Zero crashes, all failures logged

