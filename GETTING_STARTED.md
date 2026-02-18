# Getting Started - ExamForms.org

## Quick Start Guide for Development

---

## Prerequisites

### Required Software
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Git
- Node.js 18+ (if using Next.js frontend)

### Recommended Tools
- VS Code or PyCharm
- Postman (API testing)
- DBeaver (database management)
- Chrome DevTools

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/examforms.git
cd examforms
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (for JS-heavy scraping)
playwright install chromium
```

### Step 4: Setup Database

```bash
# Create PostgreSQL database
createdb examforms

# Or using psql
psql -U postgres
CREATE DATABASE examforms;
CREATE USER examforms_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE examforms TO examforms_user;
\q
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Minimum required settings for local dev**:
```env
DB_NAME=examforms
DB_USER=examforms_user
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=your-local-dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 6: Run Migrations

```bash
# Create database tables
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Step 7: Load Initial Data (Optional)

```bash
# Load sample exam data
python manage.py loaddata fixtures/sample_exams.json
```

### Step 8: Start Development Server

```bash
# Start Django development server
python manage.py runserver

# Access at: http://localhost:8000
# Admin panel: http://localhost:8000/admin
```

### Step 9: Start Celery Workers (Separate Terminal)

```bash
# Terminal 2: Start Celery worker
celery -A examforms worker -l info

# Terminal 3: Start Celery beat (scheduler)
celery -A examforms beat -l info
```

### Step 10: Start Redis (If not running)

```bash
# Terminal 4: Start Redis
redis-server
```

---

## Project Structure

```
examforms/
├── docs/                          # Documentation
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── FINANCIAL_PROJECTIONS.md
│   ├── DATA_SOURCES.md
│   ├── SEO_STRATEGY.md
│   ├── IMPLEMENTATION_ROADMAP.md
│   ├── PITCH_DECK_OUTLINE.md
│   └── ADSENSE_OPTIMIZATION_GUIDE.md
│
├── src/                           # Source code
│   ├── scrapers/                  # Web scrapers
│   │   ├── base_scraper.py
│   │   ├── upsc_scraper.py
│   │   ├── ssc_scraper.py
│   │   └── ...
│   │
│   ├── database/                  # Database models
│   │   ├── models.py
│   │   └── ...
│   │
│   ├── page_generator/            # Page generation
│   │   ├── template_generator.py
│   │   └── ...
│   │
│   ├── api/                       # API endpoints (future)
│   │   └── ...
│   │
│   └── utils/                     # Utility functions
│       └── ...
│
├── templates/                     # HTML templates
│   ├── base.html
│   ├── pages/
│   └── components/
│
├── static/                        # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── fixtures/                      # Sample data
│   └── sample_exams.json
│
├── tests/                         # Test files
│   └── ...
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore
├── README.md                      # Project overview
├── PROJECT_REPORT.md              # Business plan
├── DEPLOYMENT_GUIDE.md            # Deployment instructions
└── GETTING_STARTED.md             # This file
```

---

## Running Your First Scraper

### Test UPSC Scraper

```bash
# Activate virtual environment
source venv/bin/activate

# Run scraper manually
scrapy crawl upsc

# Or using Python script
python -m src.scrapers.upsc_scraper
```

### Check Scraped Data

```bash
# Access Django shell
python manage.py shell

# Query scraped data
from src.database.models import Exam, ExamEvent

# List all exams
exams = Exam.objects.all()
for exam in exams:
    print(exam.name)

# List recent events
events = ExamEvent.objects.order_by('-created_at')[:10]
for event in events:
    print(f"{event.exam.name} - {event.event_type}")
```

---

## Generate Your First Pages

### Using Page Generator

```python
# In Django shell or script
from src.page_generator.template_generator import PageGenerator
from src.database.models import Exam, ExamEvent

# Initialize generator
generator = PageGenerator()

# Get exam and event data
exam = Exam.objects.get(slug='upsc-civil-services')
event = ExamEvent.objects.filter(exam=exam, event_type='notification').first()

# Generate page context
context = generator.generate_notification_page(
    exam_data={
        'name': exam.name,
        'slug': exam.slug,
        'organization': exam.organization
    },
    event_data={
        'year': event.year,
        'notification_date': event.notification_date,
        'application_start': event.application_start,
        'application_end': event.application_end,
        'exam_date': event.exam_date,
        'pdf_link': event.pdf_link,
        'official_link': event.official_link
    }
)

# Context now contains all data for rendering
print(context['title'])
print(context['meta_description'])
```

---

## Development Workflow

### Daily Development Cycle

1. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/add-banking-scrapers
   ```

3. **Make Changes**
   - Write code
   - Test locally
   - Fix bugs

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add IBPS and SBI scrapers"
   ```

6. **Push to Remote**
   ```bash
   git push origin feature/add-banking-scrapers
   ```

7. **Create Pull Request**
   - Review code
   - Merge to main

---

## Common Development Tasks

### Add a New Scraper

```bash
# 1. Create new scraper file
touch src/scrapers/ibps_scraper.py

# 2. Extend BaseExamScraper
# (See src/scrapers/upsc_scraper.py as example)

# 3. Test scraper
scrapy crawl ibps

# 4. Verify data in database
python manage.py shell
>>> from src.database.models import Exam
>>> Exam.objects.filter(organization__contains='IBPS')
```

### Add a New Page Template

```bash
# 1. Create template file
touch templates/pages/cutoff.html

# 2. Add generation method in template_generator.py
# def generate_cutoff_page(self, exam_data, cutoff_data):
#     ...

# 3. Create URL route
# 4. Test rendering
```

### Add Database Fields

```bash
# 1. Modify models.py
# Add new field to model class

# 2. Create migration
python manage.py makemigrations

# 3. Apply migration
python manage.py migrate

# 4. Update scrapers to populate new field
```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test

```bash
pytest tests/test_scrapers.py
```

### Test Coverage

```bash
pytest --cov=src --cov-report=html
```

### Manual Testing Checklist

- [ ] Scraper runs without errors
- [ ] Data saves to database correctly
- [ ] Pages generate with correct data
- [ ] Links work correctly
- [ ] Mobile responsive
- [ ] Page speed < 2 seconds
- [ ] No console errors

---

## Debugging Tips

### Debug Scraper Issues

```python
# Add to scraper
import pdb; pdb.set_trace()

# Or use logging
self.logger.info(f"Scraped: {exam_name}")
self.logger.error(f"Failed to parse: {response.url}")
```

### Debug Database Issues

```bash
# Check database connection
python manage.py dbshell

# View recent migrations
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name 0001_previous_migration
```

### Debug Page Generation

```bash
# Check page context
python manage.py shell
>>> from src.page_generator.template_generator import PageGenerator
>>> generator = PageGenerator()
>>> context = generator.generate_notification_page(exam_data, event_data)
>>> print(context)
```

---

## Performance Optimization

### Database Query Optimization

```python
# Bad: N+1 queries
exams = Exam.objects.all()
for exam in exams:
    print(exam.events.all())  # Queries database each time

# Good: Select related
exams = Exam.objects.prefetch_related('events').all()
for exam in exams:
    print(exam.events.all())  # Uses cached data
```

### Caching

```python
from django.core.cache import cache

# Set cache
cache.set('exam_list', exams, timeout=3600)

# Get cache
exams = cache.get('exam_list')
if not exams:
    exams = Exam.objects.all()
    cache.set('exam_list', exams, timeout=3600)
```

---

## Useful Commands

### Django Commands

```bash
# Create app
python manage.py startapp app_name

# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check
```

### Database Commands

```bash
# Backup database
pg_dump examforms > backup.sql

# Restore database
psql examforms < backup.sql

# Reset database
python manage.py flush

# Drop and recreate
dropdb examforms
createdb examforms
python manage.py migrate
```

### Git Commands

```bash
# Check status
git status

# Create branch
git checkout -b feature-name

# Commit changes
git add .
git commit -m "Message"

# Push changes
git push origin branch-name

# Pull latest
git pull origin main

# Merge branch
git checkout main
git merge feature-name
```

---

## Environment Setup for Team Members

### New Developer Onboarding

```bash
# Day 1: Setup
1. Install prerequisites (Python, PostgreSQL, Redis)
2. Clone repository
3. Setup virtual environment
4. Install dependencies
5. Configure database
6. Run migrations
7. Start dev server

# Day 2: Understand codebase
1. Read PROJECT_REPORT.md
2. Review database models
3. Study scraper architecture
4. Test running scrapers

# Day 3: First task
1. Pick a simple scraper to add
2. Implement and test
3. Create pull request
```

### Code Review Checklist

**Before Submitting PR**:
- [ ] Code follows project style
- [ ] Tests pass
- [ ] No debug code left
- [ ] Comments added for complex logic
- [ ] Documentation updated if needed

**During Code Review**:
- [ ] Logic is correct
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Error handling is proper

---

## Troubleshooting

### Problem: Can't connect to database

**Solution**:
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Start if not running
sudo service postgresql start

# Check credentials in .env
# Test connection
psql -U examforms_user -d examforms -h localhost
```

### Problem: Migrations fail

**Solution**:
```bash
# Check migration status
python manage.py showmigrations

# Try fake migration
python manage.py migrate --fake app_name migration_number

# Last resort: Reset migrations
# (Only in development!)
python manage.py migrate app_name zero
rm app_name/migrations/000*.py
python manage.py makemigrations
python manage.py migrate
```

### Problem: Scraper not working

**Solution**:
```bash
# Check website is accessible
curl -I https://upsc.gov.in

# Run scraper with verbose logging
scrapy crawl upsc -L DEBUG

# Check CSS selectors (websites change)
scrapy shell "https://upsc.gov.in"
>>> response.css('.notification-item').getall()
```

### Problem: Page loads slowly

**Solution**:
```bash
# Profile queries
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import override_settings
>>> # Run your query
>>> print(len(connection.queries))
>>> print(connection.queries)

# Enable Django Debug Toolbar
# Check static file serving
# Use CDN for assets
```

---

## Next Steps

After completing local setup:

1. **Learn the Codebase** (1-2 days)
   - Read all documentation
   - Study existing scrapers
   - Understand page generation

2. **Build First Scraper** (2-3 days)
   - Choose an exam board
   - Implement scraper
   - Test and verify data

3. **Create First Pages** (2-3 days)
   - Generate pages from scraped data
   - Test on localhost
   - Optimize for speed

4. **Deploy to Staging** (1 day)
   - Setup staging server
   - Deploy code
   - Test end-to-end

5. **Production Launch** (1 day)
   - Setup production server
   - Configure DNS
   - Launch!

---

## Resources

### Documentation
- [PROJECT_REPORT.md](PROJECT_REPORT.md) - Complete business plan
- [TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md) - System design
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment instructions

### External Resources
- Django Docs: https://docs.djangoproject.com
- Scrapy Docs: https://docs.scrapy.org
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Redis Docs: https://redis.io/docs/

### Community
- Project Issues: GitHub Issues
- Team Chat: [Your chat platform]
- Email: [Your email]

---

## Support

### Getting Help

1. **Check Documentation**: Most questions answered here
2. **Search Issues**: GitHub Issues
3. **Ask Team**: Team chat
4. **Create Issue**: If bug or feature request

### Reporting Bugs

**Include**:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages
- Environment (OS, Python version, etc.)

---

## Contributing

We welcome contributions! 

**How to Contribute**:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Write tests
5. Submit pull request

**Code Style**:
- Follow PEP 8
- Use meaningful variable names
- Add docstrings
- Comment complex logic

---

## License

[Add your license here]

---

## Contact

- **Website**: https://examforms.org
- **Email**: contact@examforms.org
- **GitHub**: https://github.com/yourusername/examforms

---

**Happy Coding! 🚀**
