# ExamForms.org - Database Documentation

## Overview

Production-ready PostgreSQL database schema for a multi-billion dollar education information platform.

**Database**: PostgreSQL 15+  
**Timezone**: UTC (all timestamps)  
**Character Set**: UTF-8  
**Expected Scale**: 500M+ page views/month, 10M+ records  

---

## Quick Start

### 1. Create Database

```bash
# Create database
createdb examforms

# Or using psql
psql -U postgres
CREATE DATABASE examforms;
\q
```

### 2. Run Migrations

```bash
# Run migrations in order
psql -U postgres -d examforms -f migrations/001_create_core_tables.sql
psql -U postgres -d examforms -f migrations/002_create_supporting_tables.sql
psql -U postgres -d examforms -f migrations/003_create_monitoring_tables.sql
psql -U postgres -d examforms -f migrations/004_create_international_tables.sql
psql -U postgres -d examforms -f migrations/005_create_views_and_functions.sql

# Optional: Load sample data (DEVELOPMENT ONLY)
psql -U postgres -d examforms -f migrations/006_sample_data.sql
```

### 3. Verify Installation

```sql
-- Check tables created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Should show 16 tables:
-- exams, exam_events, eligibility, exam_patterns, results
-- page_metadata, scraper_logs, status_change_events, monitoring_config
-- alert_log, manual_review_queue, user_feedback
-- international_scholarships, international_fellowships, international_programs
-- universities
```

---

## Database Schema

### Core Tables (6)

#### 1. exams
Master table for all competitive exams.

**Key Fields**:
- `id`: Primary key
- `slug`: URL-friendly unique identifier (e.g., `upsc-civil-services`)
- `category`: Central Government, State Government, Banking, Defense, etc.
- `status`: active, cancelled, postponed, completed, suspended

**Indexes**: 
- `slug` (unique)
- `organization`, `category`, `status`
- Full-text search on `name` and `organization`

**Constraints**:
- `name` and `organization` cannot be empty
- `slug` must match pattern `^[a-z0-9-]+$`
- `status` must be valid enum value

---

#### 2. exam_events
Specific events/stages for each exam (notifications, forms, admit cards, results).

**Key Fields**:
- `exam_id`: Foreign key to exams
- `year`: Exam year (2020-2030)
- `event_type`: notification, application_form, admit_card, result, etc.
- `application_start/end`: Application dates
- `exam_date`: Exam date
- `details`: JSONB for flexible metadata

**Indexes**:
- `exam_id`, `year`, `event_type`
- Composite: `(exam_id, year, event_type)` unique
- Upcoming events: filtered index for active/upcoming events

**Constraints**:
- `application_start <= application_end`
- `exam_date <= exam_end_date`
- Unique per `(exam_id, year, event_type)`

---

#### 3. eligibility
Eligibility criteria for each exam.

**Key Fields**:
- `exam_id`, `year`
- `min_age`, `max_age`
- `age_relaxation`: JSONB (category-wise: OBC, SC, ST, PwD)
- `education_qualification`
- `physical_standards`: JSONB (for defense/police)

**Constraints**:
- `min_age <= max_age`
- Unique per `(exam_id, year)`

---

#### 4. exam_patterns
Exam pattern, syllabus, marking scheme.

**Key Fields**:
- `sections`: JSONB array with marks, questions, time per section
- `negative_marking`: boolean
- `total_marks`, `duration_minutes`
- `exam_mode`: Online, Offline, CBT, etc.

**Constraints**:
- Unique per `(exam_id, year)`

---

#### 5. results
Exam results and cutoff marks.

**Key Fields**:
- `exam_event_id`: Foreign key to exam_events
- `cutoff_general/ews/obc/sc/st`: Category-wise cutoffs
- `total_appeared`, `total_qualified`
- `category_stats`: JSONB with detailed statistics
- `additional_cutoffs`: JSONB (state-wise, post-wise)

**Constraints**:
- `total_qualified <= total_appeared`
- Unique per exam_event

---

#### 6. page_metadata
SEO metadata for all generated pages.

**Key Fields**:
- `page_type`: notification, admit_card, result, etc.
- `slug`: Unique URL slug
- `title` (max 60 chars), `meta_description` (max 160 chars)
- `schema_markup`: JSONB (JSON-LD structured data)
- `page_views`, `unique_visitors`: Analytics
- `needs_regeneration`: Flag to trigger page rebuild

**Indexes**:
- `slug` (unique)
- `page_type`, `exam_id`
- Full-text search on `title`
- Filtered indexes for published and needs_regeneration

---

### Monitoring Tables (5)

#### 7. scraper_logs
Track all scraping operations.

**Purpose**: Monitor scraper health, debug failures, calculate success rates.

**Key Fields**:
- `scraper_name`, `exam_id`
- `status`: success, failed, blocked, timeout
- `items_scraped`, `items_inserted`, `items_updated`
- `duration_seconds`, `retry_count`
- `error_message`, `error_trace`

---

#### 8. status_change_events
Track exam status changes (cancellations, postponements).

**Purpose**: Auto-detect and log all status changes.

**Key Fields**:
- `exam_id`, `old_status`, `new_status`
- `change_type`: CANCELLED, POSTPONED, RESCHEDULED
- `confidence_score` (0-100): Detection confidence
- `verification_status`: PENDING, APPROVED, REJECTED
- `keywords_found`: Array of trigger keywords

---

#### 9. monitoring_config
Configuration for monitoring each exam.

**Purpose**: Define which URLs to monitor and how often.

**Key Fields**:
- `exam_id`, `urls_to_monitor` (array)
- `check_frequency_minutes`: How often to check
- `priority`: LOW, MEDIUM, HIGH, CRITICAL
- `last_checked`, `last_content_hash`
- `consecutive_failures`: Track scraper failures

---

#### 10. alert_log
Log of all alerts sent to administrators.

**Purpose**: Track notifications, ensure delivery, measure response time.

**Key Fields**:
- `event_id`, `exam_id`
- `alert_type`: EMAIL, SMS, DASHBOARD, SLACK
- `alert_level`: INFO, WARNING, ERROR, CRITICAL
- `sent_to` (array), `sent_at`
- `acknowledged`, `acknowledged_by`

---

#### 11. manual_review_queue
Items requiring manual verification.

**Purpose**: Queue low-confidence detections for human review.

**Key Fields**:
- `event_id` (references status_change_events)
- `assigned_to`, `priority`
- `sla_minutes`, `due_at` (auto-calculated)
- `status`: PENDING, IN_PROGRESS, REVIEWED
- `review_decision`: APPROVED, REJECTED, MODIFIED

---

### International Tables (4)

#### 12. international_scholarships
International scholarships for Indian students.

**Key Fields**:
- `country`, `organization`, `scholarship_type`
- `level`: UNDERGRADUATE, MASTERS, PHD, POSTDOC
- `amount_per_year`, `duration_years`
- `covers_tuition/living/travel`: Coverage flags
- `language_requirements`: JSONB (IELTS, TOEFL scores)
- `application_deadline`

---

#### 13. international_fellowships
Research and professional fellowships.

**Key Fields**:
- `fellowship_type`: RESEARCH, PROFESSIONAL, POSTDOCTORAL
- `career_stage`: EARLY_CAREER, MID_CAREER, SENIOR
- `monthly_stipend`, `duration_months`

---

#### 14. international_programs
Summer schools, internships, competitions, etc.

**Key Fields**:
- `program_type`: SUMMER_SCHOOL, INTERNSHIP, HACKATHON, etc.
- `is_funded`, `is_paid`
- `duration_weeks`

---

#### 15. universities
University profiles for international opportunities.

**Key Fields**:
- `country`, `city`
- `world_rank`, `country_rank`
- `total_students`, `international_students`, `indian_students`

---

### User Feedback (1)

#### 16. user_feedback
User-reported issues and corrections.

**Purpose**: Allow users to report errors, broken links, outdated info.

**Key Fields**:
- `exam_id`, `page_slug`
- `feedback_type`: CORRECTION, MISSING_INFO, BROKEN_LINK
- `status`: NEW, IN_REVIEW, RESOLVED
- `user_email` (optional - anonymous allowed)

---

## Views & Functions

### Views

#### 1. active_exams_with_latest_events
Active exams with their most recent event details.

```sql
SELECT * FROM active_exams_with_latest_events 
WHERE category = 'Central Government'
LIMIT 10;
```

#### 2. upcoming_deadlines
All application and exam deadlines in next 30 days.

```sql
SELECT * FROM upcoming_deadlines 
ORDER BY deadline_date ASC;
```

#### 3. scraper_health_dashboard
Scraper performance metrics (last 7 days).

```sql
SELECT * FROM scraper_health_dashboard 
WHERE success_rate < 90;
```

#### 4. pending_reviews
Items in manual review queue ordered by priority.

```sql
SELECT * FROM pending_reviews 
WHERE is_overdue = true;
```

---

### Materialized Views

#### 1. exam_statistics
Aggregated statistics per exam (refresh daily).

```sql
-- Refresh manually
SELECT refresh_exam_statistics();

-- Query
SELECT * FROM exam_statistics 
WHERE total_page_views > 10000 
ORDER BY total_page_views DESC;
```

#### 2. popular_pages
Top 1000 most visited pages.

```sql
SELECT * FROM popular_pages 
WHERE page_type = 'admit_card'
LIMIT 20;
```

---

### Utility Functions

#### 1. get_exam_timeline(exam_id, year)
Get chronological timeline of all events.

```sql
SELECT * FROM get_exam_timeline(1, 2026);
```

#### 2. mark_pages_for_regeneration(exam_id)
Mark all pages for an exam to be regenerated.

```sql
SELECT mark_pages_for_regeneration(1);
-- Returns: number of pages marked
```

#### 3. get_similar_exams(exam_id, limit)
Find similar exams based on category and organization.

```sql
SELECT * FROM get_similar_exams(1, 5);
```

#### 4. search_exams(query, limit)
Full-text search with ranking.

```sql
SELECT * FROM search_exams('civil services upsc', 10);
```

#### 5. get_exam_analytics(exam_id)
Get analytics summary JSON.

```sql
SELECT get_exam_analytics(1);
-- Returns: {"total_events": 10, "total_page_views": 50000, ...}
```

#### 6. cleanup_old_scraper_logs(retention_days)
Delete old scraper logs.

```sql
-- Delete logs older than 90 days
SELECT cleanup_old_scraper_logs(90);
-- Returns: number of rows deleted
```

#### 7. get_monitoring_due_list()
Get exams due for monitoring check.

```sql
SELECT * FROM get_monitoring_due_list() 
ORDER BY priority, minutes_overdue DESC;
```

---

## Performance Optimizations

### Indexes

**Total Indexes**: 80+

**Critical Indexes**:
- All foreign keys indexed
- Unique constraints on `slug` fields
- Composite indexes on frequently queried combinations
- Partial indexes for filtered queries (e.g., `is_active = true`)
- GIN indexes for full-text search
- GIN indexes for JSONB fields
- GIN indexes for array fields

### Query Performance

**Expected Performance**:
- Simple lookups by ID: < 1ms
- Lookups by slug: < 5ms
- Complex joins (exam + events): < 20ms
- Full-text search: < 50ms
- Materialized view queries: < 10ms

**Monitoring**:
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
WHERE mean_exec_time > 100 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
WHERE idx_scan = 0 
ORDER BY tablename;
```

---

## Data Integrity

### Constraints Summary

**Check Constraints**: 50+
- Age ranges (`min_age <= max_age`)
- Date validations (`start_date <= end_date`)
- Enum validations (status, category, etc.)
- Positive numbers (fees, marks, etc.)
- String patterns (slugs must be lowercase-hyphenated)

**Foreign Keys**: All relationships properly constrained
- `ON DELETE CASCADE` for dependent data
- `ON DELETE SET NULL` for soft references

**Unique Constraints**: 
- Single-column: `slug` fields
- Multi-column: `(exam_id, year, event_type)`

**NOT NULL**: All critical fields marked as NOT NULL

---

## Triggers

### Auto-Update Timestamps

All tables with `updated_at` column have triggers to auto-update.

```sql
-- Automatically updates `updated_at` on every UPDATE
CREATE TRIGGER trigger_exams_updated_at
    BEFORE UPDATE ON exams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Auto-Calculate Due Dates

Manual review queue automatically calculates `due_at`:

```sql
-- Sets due_at = created_at + sla_minutes
CREATE TRIGGER trigger_review_queue_due_date
    BEFORE INSERT ON manual_review_queue
    FOR EACH ROW
    EXECUTE FUNCTION set_review_due_date();
```

---

## Maintenance

### Daily Tasks

```sql
-- Refresh materialized views
SELECT refresh_exam_statistics();

-- Cleanup old logs (keep 90 days)
SELECT cleanup_old_scraper_logs(90);

-- Update statistics for query planner
ANALYZE;
```

### Weekly Tasks

```sql
-- Reindex for performance
REINDEX DATABASE examforms;

-- Check for bloat
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Monthly Tasks

```sql
-- Full vacuum analyze
VACUUM FULL ANALYZE;

-- Check for unused indexes
SELECT * FROM pg_stat_user_indexes 
WHERE idx_scan = 0;
```

---

## Backup & Recovery

### Backup Script

```bash
#!/bin/bash
# Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/examforms"

# Full backup
pg_dump -U postgres -Fc examforms > "$BACKUP_DIR/examforms_$DATE.dump"

# Upload to S3
aws s3 cp "$BACKUP_DIR/examforms_$DATE.dump" \
    s3://examforms-backups/database/

# Keep only last 7 days locally
find "$BACKUP_DIR" -name "examforms_*.dump" -mtime +7 -delete
```

### Restore

```bash
# Restore from backup
pg_restore -U postgres -d examforms_new examforms_20260129.dump

# Or from SQL dump
psql -U postgres examforms < backup.sql
```

---

## Security

### Access Control

```sql
-- Create read-only user for analytics
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE examforms TO analytics_user;
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;

-- Create scraper user (read/write to specific tables)
CREATE USER scraper_user WITH PASSWORD 'secure_password';
GRANT INSERT, UPDATE ON exams, exam_events, scraper_logs TO scraper_user;
```

### Sensitive Data

**No sensitive user data stored**:
- No passwords (no user authentication)
- User feedback: email is optional
- IP addresses: stored for debugging only

**Admin data**:
- Store hashed passwords for admin users (in separate auth table)
- Use environment variables for database credentials

---

## Scaling Strategy

### Current Capacity

**Expected with default configuration**:
- Exams: 10,000+
- Exam Events: 100,000+
- Pages: 500,000+
- Page Views: 500M+/month
- Scraper Logs: 10M+ (with cleanup)

### When to Scale

**Vertical Scaling** (increase server resources):
- When CPU > 70% consistently
- When memory > 80%
- When disk I/O is bottleneck

**Horizontal Scaling** (add read replicas):
- When read queries > 10,000/second
- When single server can't handle load
- Setup: 1 primary (write) + 2-3 replicas (read)

**Sharding** (partition data):
- Not needed until 50M+ exams or 1B+ page views/month
- If needed: shard by `category` or `year`

---

## Troubleshooting

### Common Issues

#### 1. Slow Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1s
SELECT pg_reload_conf();

-- Check slow queries
SELECT * FROM pg_stat_statements 
WHERE mean_exec_time > 1000 
ORDER BY mean_exec_time DESC;
```

**Solutions**:
- Add missing indexes
- Rewrite query
- Use materialized views

---

#### 2. Disk Space Full

```sql
-- Check database size
SELECT pg_database.datname, 
       pg_size_pretty(pg_database_size(pg_database.datname)) 
FROM pg_database;

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Solutions**:
- Run `cleanup_old_scraper_logs()`
- Archive old data
- Increase disk space

---

#### 3. Connection Limit Reached

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
  AND state_change < NOW() - INTERVAL '5 minutes';
```

**Solutions**:
- Increase `max_connections` in postgresql.conf
- Use connection pooling (PgBouncer)
- Close connections properly in code

---

## Testing

### Data Validation Tests

```sql
-- Test 1: No orphaned exam_events
SELECT COUNT(*) FROM exam_events ee 
LEFT JOIN exams e ON ee.exam_id = e.id 
WHERE e.id IS NULL;
-- Expected: 0

-- Test 2: All slugs are unique
SELECT slug, COUNT(*) FROM exams 
GROUP BY slug HAVING COUNT(*) > 1;
-- Expected: 0 rows

-- Test 3: Date constraints valid
SELECT COUNT(*) FROM exam_events 
WHERE application_start > application_end;
-- Expected: 0

-- Test 4: All pages have valid exam references
SELECT COUNT(*) FROM page_metadata pm 
LEFT JOIN exams e ON pm.exam_id = e.id 
WHERE pm.exam_id IS NOT NULL AND e.id IS NULL;
-- Expected: 0
```

---

## Migration History

| Version | Date | Description |
|---------|------|-------------|
| 001 | 2026-01-29 | Core tables (exams, exam_events) |
| 002 | 2026-01-29 | Supporting tables (eligibility, patterns, results) |
| 003 | 2026-01-29 | Monitoring tables (status changes, alerts) |
| 004 | 2026-01-29 | International opportunities tables |
| 005 | 2026-01-29 | Views and utility functions |
| 006 | 2026-01-29 | Sample data (development only) |

---

## Contact & Support

**Issues**: GitHub Issues  
**Email**: dev@examforms.org  
**Documentation**: See `/docs` folder

---

**Database Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: January 29, 2026

