# Technical Architecture - ExamForms.org

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER TRAFFIC                          │
│              (Google Search, Discover, Direct)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE CDN                            │
│              (Caching, DDoS Protection, SSL)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   WEB APPLICATION                            │
│              (Next.js / Django + Templates)                  │
│                 ┌──────────────────┐                         │
│                 │  Page Generator  │                         │
│                 │  (Programmatic)  │                         │
│                 └──────────────────┘                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │    Redis     │  │ Elasticsearch│      │
│  │ (Exam Data)  │  │   (Cache)    │  │  (Search)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                      ▲
                      │
┌─────────────────────────────────────────────────────────────┐
│              DATA COLLECTION PIPELINE                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │           Scraping Orchestrator                  │       │
│  │              (Apache Airflow)                    │       │
│  └──────────────────────────────────────────────────┘       │
│         │              │              │                      │
│         ▼              ▼              ▼                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Scrapy   │  │Puppeteer │  │ API      │                  │
│  │ Spiders  │  │ Scripts  │  │ Clients  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│         │              │              │                      │
│         └──────────────┴──────────────┘                      │
│                        │                                      │
│                        ▼                                      │
│              ┌──────────────────┐                            │
│              │ Data Validator   │                            │
│              │ & Normalizer     │                            │
│              └──────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 EXTERNAL SOURCES                             │
│  • 500+ Government Websites                                  │
│  • Exam Board Portals                                        │
│  • Official Notification Pages                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Web Scraping System

**Technology**: Python + Scrapy + Puppeteer

**Architecture**:
```python
scrapers/
├── spiders/
│   ├── upsc_spider.py
│   ├── ssc_spider.py
│   ├── ibps_spider.py
│   └── ... (500+ spiders)
├── parsers/
│   ├── date_parser.py
│   ├── pdf_extractor.py
│   └── link_validator.py
├── middleware/
│   ├── proxy_rotation.py
│   ├── rate_limiter.py
│   └── retry_handler.py
└── pipelines/
    ├── validation_pipeline.py
    ├── deduplication_pipeline.py
    └── database_pipeline.py
```

**Scheduling**:
- Apache Airflow DAGs
- Critical sources: Every 2 hours
- Regular sources: Daily
- Static content: Weekly

**Example Scraper Logic**:
```python
class UPSCSpider(scrapy.Spider):
    name = 'upsc'
    start_urls = ['https://upsc.gov.in/']
    
    def parse(self, response):
        # Extract notification links
        notifications = response.css('.notification-item')
        
        for notif in notifications:
            yield {
                'exam_name': notif.css('.title::text').get(),
                'notification_date': parse_date(notif.css('.date::text').get()),
                'pdf_link': notif.css('a::attr(href)').get(),
                'source_url': response.url,
                'scraped_at': datetime.now()
            }
```

### 2. Database Schema

**PostgreSQL Schema**:

```sql
-- Main Exams Table
CREATE TABLE exams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    organization VARCHAR(255),
    category VARCHAR(100), -- Central/State/University/Banking
    exam_type VARCHAR(100), -- Recruitment/Scholarship/Fellowship
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Exam Events (Notifications, Forms, Admit Cards, etc.)
CREATE TABLE exam_events (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER REFERENCES exams(id),
    year INTEGER NOT NULL,
    event_type VARCHAR(50), -- notification/form/admit_card/result/answer_key
    event_date DATE,
    application_start DATE,
    application_end DATE,
    exam_date DATE,
    status VARCHAR(50), -- upcoming/active/completed
    official_link TEXT,
    pdf_link TEXT,
    details JSONB, -- Flexible metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Eligibility Criteria
CREATE TABLE eligibility (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER REFERENCES exams(id),
    year INTEGER,
    min_age INTEGER,
    max_age INTEGER,
    education_qualification TEXT,
    nationality TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Exam Pattern
CREATE TABLE exam_patterns (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER REFERENCES exams(id),
    year INTEGER,
    total_marks INTEGER,
    duration_minutes INTEGER,
    sections JSONB, -- [{name, marks, questions}]
    negative_marking BOOLEAN,
    pattern_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Results & Cutoffs
CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    exam_event_id INTEGER REFERENCES exam_events(id),
    result_date DATE,
    cutoff_general DECIMAL,
    cutoff_obc DECIMAL,
    cutoff_sc DECIMAL,
    cutoff_st DECIMAL,
    cutoff_ews DECIMAL,
    total_appeared INTEGER,
    total_qualified INTEGER,
    result_pdf_link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- SEO Metadata
CREATE TABLE page_metadata (
    id SERIAL PRIMARY KEY,
    page_type VARCHAR(50),
    exam_id INTEGER REFERENCES exams(id),
    year INTEGER,
    slug VARCHAR(500) UNIQUE,
    title VARCHAR(255),
    meta_description TEXT,
    canonical_url TEXT,
    schema_markup JSONB,
    last_crawled TIMESTAMP,
    page_views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_exams_slug ON exams(slug);
CREATE INDEX idx_exam_events_exam_year ON exam_events(exam_id, year);
CREATE INDEX idx_exam_events_type ON exam_events(event_type);
CREATE INDEX idx_page_metadata_slug ON page_metadata(slug);
```

### 3. Page Generation System

**Template Structure**:

```
templates/
├── base.html
├── pages/
│   ├── notification.html
│   ├── application.html
│   ├── admit_card.html
│   ├── result.html
│   ├── answer_key.html
│   ├── syllabus.html
│   ├── exam_pattern.html
│   ├── eligibility.html
│   └── cutoff.html
└── components/
    ├── header.html
    ├── breadcrumbs.html
    ├── related_links.html
    ├── important_dates_table.html
    └── faq.html
```

**Dynamic Page Generation Logic**:

```python
def generate_admit_card_page(exam_id, year):
    """
    Generate admit card page for specific exam and year
    """
    exam = get_exam(exam_id)
    event = get_exam_event(exam_id, year, 'admit_card')
    
    context = {
        'exam_name': exam.name,
        'year': year,
        'admit_card_date': event.event_date,
        'exam_date': event.exam_date,
        'download_link': event.official_link,
        'important_dates': get_important_dates(exam_id, year),
        'how_to_download': generate_steps(exam),
        'related_pages': get_related_pages(exam_id, year),
        'faqs': generate_faqs(exam, 'admit_card'),
        'schema_markup': generate_schema(exam, event, 'admit_card')
    }
    
    return render_template('pages/admit_card.html', context)
```

**URL Structure**:
```
/[exam-slug]-[year]-notification
/[exam-slug]-[year]-application-form
/[exam-slug]-[year]-admit-card
/[exam-slug]-[year]-answer-key
/[exam-slug]-[year]-result
/[exam-slug]-[year]-cutoff
/[exam-slug]-syllabus
/[exam-slug]-exam-pattern
/[exam-slug]-eligibility

Examples:
/upsc-civil-services-2026-notification
/ssc-cgl-2026-admit-card
/ibps-po-2026-result
```

### 4. SEO Implementation

**Structured Data (Schema.org)**:

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "UPSC Civil Services 2026 Admit Card",
  "description": "Download UPSC Civil Services Prelims 2026 Admit Card from official website",
  "startDate": "2026-06-07",
  "endDate": "2026-06-07",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "Multiple Exam Centers",
    "address": {
      "@type": "PostalAddress",
      "addressCountry": "IN"
    }
  },
  "organizer": {
    "@type": "Organization",
    "name": "Union Public Service Commission",
    "url": "https://upsc.gov.in"
  }
}
```

**FAQPage Schema**:
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "When will UPSC CSE 2026 admit card be released?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "UPSC Civil Services 2026 admit card is expected to be released 3 weeks before the exam date..."
      }
    }
  ]
}
```

**Sitemap Generation**:
```python
def generate_sitemap():
    """
    Generate XML sitemap automatically
    Updated hourly
    """
    pages = get_all_published_pages()
    
    sitemap_xml = []
    for page in pages:
        sitemap_xml.append({
            'loc': f"https://examforms.org/{page.slug}",
            'lastmod': page.updated_at.isoformat(),
            'changefreq': get_change_frequency(page.page_type),
            'priority': get_priority(page.page_type)
        })
    
    return render_sitemap_xml(sitemap_xml)

def get_change_frequency(page_type):
    # Critical pages change daily
    if page_type in ['admit_card', 'result', 'notification']:
        return 'daily'
    # Static pages change monthly
    return 'monthly'

def get_priority(page_type):
    # High priority for time-sensitive content
    if page_type in ['admit_card', 'result']:
        return 0.9
    # Medium priority for notification
    if page_type == 'notification':
        return 0.8
    # Lower priority for static content
    return 0.6
```

### 5. Caching Strategy

**Redis Caching Layers**:

```python
# Page cache (30 minutes for dynamic, 24 hours for static)
@cache_page(60 * 30)  # 30 minutes
def admit_card_view(request, exam_slug, year):
    return generate_admit_card_page(exam_slug, year)

# Database query cache
def get_exam_events(exam_id, year):
    cache_key = f"exam_events:{exam_id}:{year}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    events = db.query(ExamEvent).filter(
        exam_id=exam_id, year=year
    ).all()
    
    redis_client.setex(cache_key, 3600, json.dumps(events))
    return events

# CDN caching via Cloudflare
# Static assets: 1 year
# HTML pages: 1 hour (with stale-while-revalidate)
```

### 6. Monitoring & Analytics

**Key Metrics to Track**:

```python
metrics = {
    # Scraping Health
    'scraper_success_rate': 'Percentage of successful scrapes',
    'scraper_latency': 'Average time per scrape',
    'data_freshness': 'Time since last update per exam',
    
    # Traffic Metrics
    'page_views': 'Total page views',
    'unique_visitors': 'Unique users',
    'pages_per_session': 'Engagement depth',
    'bounce_rate': 'Single-page sessions',
    'avg_session_duration': 'Time on site',
    
    # SEO Metrics
    'indexed_pages': 'Pages in Google index',
    'avg_position': 'Average search ranking',
    'impressions': 'Search impressions',
    'ctr': 'Click-through rate',
    
    # Revenue Metrics
    'page_rpm': 'Revenue per 1000 page views',
    'ad_impressions': 'Total ad views',
    'ad_ctr': 'Ad click-through rate',
    'daily_revenue': 'AdSense earnings'
}
```

**Alerting System**:
```python
# Alert if scraper fails
if scraper_success_rate < 0.85:
    send_alert("Scraper success rate below 85%")

# Alert if traffic drops
if page_views_today < (page_views_yesterday * 0.7):
    send_alert("Traffic dropped by 30%")

# Alert if revenue drops
if rpm_today < (rpm_7day_avg * 0.8):
    send_alert("RPM dropped significantly")
```

## Deployment Architecture

### Production Environment

```yaml
# AWS/DigitalOcean Setup

Web Servers:
  - 2-4 instances (auto-scaling)
  - 4GB RAM, 2 vCPU each
  - Load balanced

Database:
  - PostgreSQL (managed service)
  - 8GB RAM, 100GB SSD
  - Daily automated backups

Cache:
  - Redis (managed service)
  - 2GB RAM

Scraping Workers:
  - 3-5 instances
  - 2GB RAM, 1 vCPU each
  - Queue-based task distribution

CDN:
  - Cloudflare (free + pro)
  - 90% cache hit rate target

Storage:
  - S3/R2 for static assets
  - PDF storage (1TB initial)
```

### Cost Estimates (Monthly)

```
Web Servers (4x): $80-160
Database: $50-100
Redis: $20-40
Scraping Workers (5x): $50-100
CDN: $20-50
Storage: $25-50
Monitoring Tools: $50
Total: $295-550/month at scale
```

## Security Considerations

1. **Rate Limiting**: Prevent scraper blocks
2. **IP Rotation**: Use proxy pools for scraping
3. **DDoS Protection**: Cloudflare + rate limiting
4. **Data Validation**: Prevent malicious data injection
5. **HTTPS**: SSL for all pages
6. **Database Security**: Encrypted connections, regular backups
7. **Access Control**: Restricted admin access, 2FA

## Performance Targets

- **Page Load Time**: < 2 seconds (mobile)
- **Time to First Byte**: < 500ms
- **Core Web Vitals**:
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1
- **Uptime**: 99.9%
- **Cache Hit Rate**: > 85%

## Scalability Plan

### Phase 1 (0-10M page views/month)
- Single database server
- 2 web servers
- 2 scraping workers

### Phase 2 (10-100M page views/month)
- Database read replicas
- 4-6 web servers (auto-scaling)
- 5 scraping workers
- Redis cluster

### Phase 3 (100M-500M page views/month)
- Database sharding by exam category
- 10-15 web servers (auto-scaling)
- 10 scraping workers
- Elasticsearch for search
- Multiple Redis instances

