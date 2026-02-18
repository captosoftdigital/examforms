# Technical Specifications & Assumptions - ExamForms.org

## Mission-Critical System Requirements

**Project Scale**: Multi-billion dollar platform
**Expected Load**: 500M+ page views/month at scale
**Uptime Requirement**: 99.99% (52 minutes downtime/year)
**Performance Requirement**: < 2 seconds page load time
**Data Accuracy**: 99.9% (critical for user trust)

---

## SECTION 1: ASSUMPTIONS & CONSTRAINTS

### 1.1 Technical Assumptions

#### Infrastructure
- **Assumption**: Using cloud infrastructure (AWS/DigitalOcean) with auto-scaling
- **Constraint**: Must handle traffic spikes of 10x normal load (exam result days)
- **Validation Needed**: Load testing with 50K concurrent users minimum
- **Failure Mode**: If servers crash, CDN serves cached pages (stale data acceptable for 5 minutes)

#### Database
- **Assumption**: PostgreSQL can handle 10M+ rows with proper indexing
- **Constraint**: Query response time must be < 100ms for 95% of queries
- **Validation Needed**: Database stress testing with 20M records
- **Failure Mode**: Read replicas for failover, cache layer prevents database overload

#### Scraping
- **Assumption**: Government websites have stable HTML structure for 80% uptime
- **Constraint**: Websites may block if > 1 request per 5 seconds
- **Validation Needed**: Test scrapers detect structural changes automatically
- **Failure Mode**: If scraper fails, mark as "pending verification", alert admin

#### Caching
- **Assumption**: Redis can cache hot data with 1GB+ memory
- **Constraint**: Cache invalidation within 5 minutes of data change
- **Validation Needed**: Cache hit rate > 85%
- **Failure Mode**: If Redis fails, system slows but remains functional (direct DB queries)

### 1.2 Data Assumptions

#### Source Reliability
- **Assumption**: Official government websites are authoritative (no verification needed)
- **Constraint**: Non-official sources require 2+ confirmations
- **Validation Needed**: Source credibility scoring system
- **Failure Mode**: If source unreliable, flag for manual review

#### Update Frequency
- **Assumption**: Exam data changes at most once per day for 90% of exams
- **Constraint**: Critical exams (UPSC, SSC) may change multiple times daily
- **Validation Needed**: Track actual change frequency over 3 months
- **Failure Mode**: If updates missed, auto-recovery on next scrape cycle

#### Data Completeness
- **Assumption**: Not all data fields will be available for all exams
- **Constraint**: Minimum viable data: exam name, organization, notification date
- **Validation Needed**: Define mandatory vs optional fields clearly
- **Failure Mode**: Partial data shown with "Data pending" labels

### 1.3 User Assumptions

#### Traffic Patterns
- **Assumption**: 85% mobile traffic, 15% desktop
- **Constraint**: Mobile-first design mandatory
- **Validation Needed**: Test on 10+ device types
- **Failure Mode**: Graceful degradation on old browsers (basic content accessible)

#### User Behavior
- **Assumption**: Average 4 pages per session
- **Constraint**: Bounce rate < 60% target
- **Validation Needed**: Analytics tracking for 3 months
- **Failure Mode**: If bounce rate high, A/B test layout improvements

#### Search Patterns
- **Assumption**: Users search long-tail keywords (e.g., "SSC CGL 2026 admit card")
- **Constraint**: Must rank top 3 for target keywords within 6 months
- **Validation Needed**: Keyword research and competitor analysis
- **Failure Mode**: If rankings low, diagnose SEO issues (technical/content/backlinks)

### 1.4 Business Assumptions

#### AdSense
- **Assumption**: RPM will be ₹150-250 for Indian education traffic
- **Constraint**: Ad density must not hurt user experience
- **Validation Needed**: A/B test ad placements over 3 months
- **Failure Mode**: If RPM low, optimize ad positions, test alternative networks

#### Growth Rate
- **Assumption**: 25-40% month-over-month traffic growth for first 12 months
- **Constraint**: Quality must not degrade with scale
- **Validation Needed**: Monitor content quality metrics
- **Failure Mode**: If growth stalls, investigate (SEO penalties, competition, technical issues)

---

## SECTION 2: SYSTEM CONDITIONS & BOUNDARIES

### 2.1 When Does This System Work?

#### ✅ Optimal Conditions
- Official websites are accessible (> 95% uptime)
- HTML structure is stable (< 5% monthly changes)
- Traffic is within provisioned capacity (< 80% CPU/memory)
- Database queries are optimized (all indexes present)
- CDN cache hit rate > 85%
- No Google algorithm penalty
- AdSense account in good standing

#### ⚠️ Degraded Mode
- Official website downtime (show cached data with timestamp)
- Scraper structural changes detected (queue manual review)
- High traffic (serve from CDN, reduce database queries)
- Database read replica lag (acceptable for non-critical data)
- Redis cache miss (slower but functional)

#### ❌ System Failure Scenarios
- **Total database failure**: Must have hot standby (failover < 5 minutes)
- **All scrapers failing**: Manual data entry mode + user notice
- **AdSense suspension**: Switch to backup network (Ezoic) immediately
- **Google Search penalty**: Must have traffic diversification (multiple domains)
- **DDoS attack**: Cloudflare protection + rate limiting

### 2.2 What Could Go Wrong?

#### Data Quality Issues
1. **Scraper extracts wrong data**
   - Detection: Confidence scoring < 70%
   - Response: Flag for manual review
   - Prevention: Test scrapers with sample data before deployment

2. **Data becomes outdated**
   - Detection: Last updated > 24 hours
   - Response: Re-scrape immediately
   - Prevention: Scheduled scraping every 6 hours for critical exams

3. **Duplicate content created**
   - Detection: Same exam slug exists
   - Response: Update existing, don't create new
   - Prevention: Unique constraints on database

4. **Wrong cancellation detected**
   - Detection: Confidence < 70% or single source only
   - Response: Manual review required
   - Prevention: Multi-source verification system

#### Performance Issues
1. **Page load time > 2 seconds**
   - Detection: Real User Monitoring (RUM)
   - Response: Optimize images, reduce JS, aggressive caching
   - Prevention: Performance budget enforcement in CI/CD

2. **Database query timeout**
   - Detection: Query time > 5 seconds
   - Response: Kill query, serve cached data
   - Prevention: Query optimization, proper indexing

3. **Scraper timeout**
   - Detection: No response in 30 seconds
   - Response: Retry with exponential backoff (max 3 attempts)
   - Prevention: Set reasonable timeouts, use proxy rotation

4. **Memory leak**
   - Detection: Memory usage growing unbounded
   - Response: Restart affected service
   - Prevention: Proper resource cleanup, monitoring

#### SEO Issues
1. **Duplicate content penalty**
   - Detection: Search Console warnings
   - Response: Canonical tags, remove duplicates
   - Prevention: Unique content per page, proper URL structure

2. **Indexing issues**
   - Detection: Coverage report in Search Console
   - Response: Fix technical SEO issues
   - Prevention: Valid sitemaps, robots.txt, proper redirects

3. **Ranking drops**
   - Detection: Position tracking
   - Response: Diagnose (technical, content, backlinks, algorithm)
   - Prevention: White-hat SEO only, monitor competitors

#### Monetization Issues
1. **AdSense policy violation**
   - Detection: Email notification
   - Response: Fix immediately, appeal if needed
   - Prevention: Regular policy compliance audits

2. **RPM drops**
   - Detection: Daily RPM tracking
   - Response: Test ad placements, check viewability
   - Prevention: A/B test ad positions monthly

3. **Low fill rate**
   - Detection: Unfilled ad inventory
   - Response: Adjust ad settings, add backup networks
   - Prevention: Multiple ad networks configured

---

## SECTION 3: ERROR HANDLING STRATEGY

### 3.1 Error Categories

#### Critical Errors (System Down)
- Database connection lost
- All web servers down
- DNS failure
- SSL certificate expired

**Response**: Immediate alert (SMS + Email + Slack), automatic failover

#### High Priority Errors (Feature Degraded)
- Scraper failing for top 10 exams
- Search functionality broken
- AdSense not loading
- Page load time > 5 seconds

**Response**: Alert within 5 minutes, investigate immediately

#### Medium Priority Errors (Acceptable Degradation)
- Individual scraper failing
- Image loading slow
- Cache miss rate high
- Non-critical page 404

**Response**: Log for investigation, fix in next deployment

#### Low Priority Errors (Cosmetic)
- CSS rendering issue on old browser
- Minor layout shift
- Non-critical feature unavailable

**Response**: Log, fix in weekly maintenance

### 3.2 Error Recovery

#### Automatic Recovery
- Scraper fails → Retry with exponential backoff (1min, 5min, 30min)
- Database query timeout → Serve from cache
- API rate limit → Queue for later, respect rate limits
- Server overload → Auto-scale up

#### Manual Intervention Required
- Data accuracy concerns → QA team review
- SEO penalty → Technical SEO audit
- AdSense suspension → Policy review + appeal
- Security breach → Incident response protocol

---

## SECTION 4: QUALITY STANDARDS

### 4.1 Code Quality

#### Must Have
- Type hints (Python 3.11+)
- Docstrings for all public functions
- Unit tests (> 80% coverage)
- Integration tests for critical paths
- Error handling for all external calls
- Logging for debugging
- Input validation

#### Testing Requirements
- Unit tests run on every commit
- Integration tests run before deployment
- Load tests weekly in staging
- Security scans monthly
- Penetration testing quarterly

### 4.2 Performance Standards

#### Page Load Time
- Desktop: < 1.5 seconds
- Mobile 4G: < 2 seconds
- Mobile 3G: < 3 seconds (acceptable)

**Measurement**: Lighthouse score > 90

#### Database Performance
- Read queries: < 50ms (95th percentile)
- Write queries: < 200ms (95th percentile)
- Complex queries: < 500ms (95th percentile)

**Measurement**: Database query logs, APM tools

#### API Response Time
- Internal APIs: < 100ms
- External APIs: < 1 second (with timeout)
- Scraping: 5-30 seconds per page (acceptable)

**Measurement**: API monitoring (Datadog, New Relic)

### 4.3 Design Standards

#### Visual Design
- Mobile-first responsive design
- Consistent color scheme (brand colors)
- Readable typography (16px minimum font)
- High contrast ratios (WCAG AA compliance)
- Fast loading (lazy load images)

#### UX Principles
- Maximum 3 clicks to any information
- Clear call-to-action buttons
- Breadcrumb navigation
- Search functionality prominent
- No intrusive ads (respects user experience)

#### Accessibility
- ARIA labels for screen readers
- Keyboard navigation support
- Alt text for all images
- Proper heading hierarchy
- No flashing content (seizure risk)

---

## SECTION 5: IMPLEMENTATION PHASES

### Phase 1: Core System (Weeks 1-4)

#### What We're Building
- Database schema implementation
- Base scraper framework
- 2 working scrapers (UPSC, SSC)
- Basic page generation
- Admin interface (minimal)

#### What We're NOT Building Yet
- Advanced features (search, filters)
- User accounts
- Comments/community features
- Mobile apps
- Advanced analytics

#### Success Criteria
- 2 scrapers working with 90% success rate
- 1,000 pages generated
- Page load time < 2 seconds
- Zero SQL injection vulnerabilities
- Admin can manually review/edit data

#### Known Limitations
- Manual deployment (no CI/CD yet)
- No caching (direct database queries)
- Basic error handling
- No monitoring (manual log checking)

### Phase 2: Scale Foundation (Weeks 5-8)

#### What We're Adding
- 10 more scrapers
- Redis caching layer
- CDN integration (Cloudflare)
- Automated deployment
- Basic monitoring (UptimeRobot)

#### Success Criteria
- 10,000 pages generated
- Cache hit rate > 70%
- Page load time < 1.5 seconds
- Automated daily scraping
- Email alerts on scraper failures

#### Known Limitations
- Manual content review still needed
- No auto-update system yet
- Basic SEO (no advanced optimization)

### Phase 3: Production Ready (Weeks 9-12)

#### What We're Adding
- Auto-update & cancellation detection
- Advanced SEO (sitemaps, schema, internal linking)
- AdSense integration
- Comprehensive monitoring
- Load balancing

#### Success Criteria
- 50,000 pages indexed
- 99.9% uptime
- Auto-detection of exam cancellations (70% confidence)
- RPM > ₹150
- Page load time < 1 second

#### Known Limitations
- Manual review queue still exists (for low confidence)
- Limited to domestic exams (international not yet)
- Single domain (multi-domain in future)

---

## SECTION 6: TECHNICAL DEBT MANAGEMENT

### Acceptable Technical Debt (For Speed)

#### Phase 1
- ✅ Hardcoded configurations (will move to config files)
- ✅ Basic error messages (will improve UX)
- ✅ Manual deployment (CI/CD in Phase 2)
- ✅ Simple authentication (will add 2FA later)

#### Must NOT Accept
- ❌ SQL injection vulnerabilities
- ❌ Exposed API keys in code
- ❌ No error handling for external calls
- ❌ No input validation
- ❌ Slow queries without indexes

### Refactoring Schedule
- After Phase 1: Code review, fix critical issues
- After Phase 2: Performance optimization
- After Phase 3: Comprehensive refactoring

---

## SECTION 7: WHAT I WILL BUILD NEXT

### Immediate: Database Schema (100% verified)
I will create the complete database schema with:
- ✅ All tables with proper types
- ✅ Foreign key constraints
- ✅ Indexes for performance
- ✅ Validation rules
- ✅ Sample data for testing

**Assumptions**:
- PostgreSQL 15+
- UTF-8 encoding
- Timezone-aware timestamps

**What could go wrong**: 
- Migration fails (solution: rollback script)
- Performance issues (solution: benchmark queries)

### Next: Base Scraper (with all error cases)
I will build the base scraper framework with:
- ✅ Retry logic (exponential backoff)
- ✅ Timeout handling
- ✅ Rate limiting
- ✅ Proxy rotation
- ✅ Error logging
- ✅ Data validation

**Assumptions**:
- Websites respond within 30 seconds
- Rate limit: 1 request per 5 seconds
- HTML structure can change (must detect)

**What could go wrong**:
- Blocked by website (solution: proxy rotation)
- Structural changes (solution: confidence scoring + alert)
- Infinite loops (solution: max retries = 3)

### After That: UPSC Scraper (battle-tested)
I will create UPSC scraper with:
- ✅ Handles 5+ page types (notifications, admit cards, results)
- ✅ PDF parsing if needed
- ✅ Date extraction (multiple formats)
- ✅ Duplicate detection
- ✅ Unit tests (mocked responses)

**Assumptions**:
- UPSC website structure as of January 2026
- Changes detected within 24 hours
- Manual review for ambiguous cases

**What could go wrong**:
- Website redesign (solution: structural change detection)
- PDFs corrupted (solution: fallback to manual)
- Dates in multiple formats (solution: fuzzy date parsing)

---

## SECTION 8: DEVELOPMENT PRINCIPLES

### Code I Will Write

#### Always
- Type hints
- Docstrings
- Input validation
- Error handling (try/except)
- Logging
- Tests for critical paths

#### Never
- Hardcoded sensitive data
- Direct database queries in views (use ORM)
- Unvalidated user input
- Synchronous blocking operations in request handlers
- Bare except clauses (catch specific exceptions)

### Testing Philosophy

#### Unit Tests
- Mock external dependencies
- Test happy path + edge cases
- Test error conditions
- Fast (< 1 second per test)

#### Integration Tests
- Test real database
- Test real HTTP calls (against test servers)
- Test end-to-end flows
- Slower (acceptable: 10-30 seconds)

#### Load Tests
- Simulate 10x normal load
- Test database under stress
- Test CDN caching
- Find breaking points

---

## SECTION 9: QUESTIONS TO ANSWER BEFORE CODING

### Architecture Questions
1. ✅ Django or FastAPI for backend? 
   - **Decision**: Django (faster development, built-in admin)
2. ✅ Monolith or microservices?
   - **Decision**: Monolith initially (microservices at scale)
3. ✅ Server-side rendering or API + frontend?
   - **Decision**: Server-side (better SEO)

### Data Questions
1. ✅ How to handle partial data?
   - **Decision**: Show what we have, mark "Pending" for missing
2. ✅ How long to keep historical data?
   - **Decision**: 3 years active, archive older
3. ✅ How to handle conflicting information?
   - **Decision**: Prefer official sources, flag conflicts

### Performance Questions
1. ✅ What to cache?
   - **Decision**: Hot pages (cache), dynamic data (no cache)
2. ✅ When to invalidate cache?
   - **Decision**: On data update or 5 minutes max age
3. ✅ Database sharding strategy?
   - **Decision**: Not yet, single database until 10M+ rows

---

## READY TO CODE?

I will now proceed to build:

1. **Complete Database Schema** with migrations
2. **Base Scraper Framework** with error handling
3. **UPSC Scraper** (fully tested)
4. **Page Generator** with templates
5. **Admin Interface** for data review

Each component will be built with:
- ✅ Complete error handling
- ✅ Comprehensive tests
- ✅ Documentation
- ✅ Performance considerations
- ✅ Security best practices

**Shall I proceed with the database schema first?**

