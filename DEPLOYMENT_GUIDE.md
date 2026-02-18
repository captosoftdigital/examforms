# Deployment Guide - ExamForms.org

## Quick Start Deployment

---

## OPTION 1: DigitalOcean Deployment (Recommended for MVP)

### Step 1: Create Droplet

```bash
# Specifications
- Ubuntu 22.04 LTS
- 4GB RAM, 2 vCPU
- 80GB SSD
- Region: Bangalore/Mumbai (for India traffic)

# Cost: $24/month
```

### Step 2: Initial Server Setup

```bash
# SSH into server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL
apt install postgresql postgresql-contrib -y

# Install Redis
apt install redis-server -y

# Install Nginx
apt install nginx -y

# Install Supervisor (for process management)
apt install supervisor -y
```

### Step 3: Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE examforms;
CREATE USER examforms_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE examforms TO examforms_user;
\q
```

### Step 4: Application Setup

```bash
# Create application directory
mkdir -p /var/www/examforms
cd /var/www/examforms

# Clone repository
git clone https://github.com/yourusername/examforms.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Copy environment file
cp .env.example .env
nano .env  # Edit with your values

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### Step 5: Nginx Configuration

```bash
# Create Nginx config
nano /etc/nginx/sites-available/examforms

# Add this configuration:
```

```nginx
server {
    listen 80;
    server_name examforms.org www.examforms.org;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name examforms.org www.examforms.org;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/examforms.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/examforms.org/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /var/www/examforms/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/examforms/media/;
        expires 1y;
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/examforms /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 6: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d examforms.org -d www.examforms.org

# Auto-renewal (already setup by certbot)
# Test renewal
certbot renew --dry-run
```

### Step 7: Application Process Management (Supervisor)

```bash
# Create supervisor config for Django/Gunicorn
nano /etc/supervisor/conf.d/examforms.conf
```

```ini
[program:examforms_web]
command=/var/www/examforms/venv/bin/gunicorn examforms.wsgi:application --bind 127.0.0.1:8000 --workers 4
directory=/var/www/examforms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/examforms/web.log

[program:examforms_celery]
command=/var/www/examforms/venv/bin/celery -A examforms worker -l info
directory=/var/www/examforms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/examforms/celery.log

[program:examforms_celery_beat]
command=/var/www/examforms/venv/bin/celery -A examforms beat -l info
directory=/var/www/examforms
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/examforms/celery_beat.log
```

```bash
# Create log directory
mkdir -p /var/log/examforms

# Update supervisor
supervisorctl reread
supervisorctl update
supervisorctl status
```

---

## OPTION 2: AWS Deployment (For Scale)

### Architecture

```
Route 53 (DNS)
    ↓
CloudFront (CDN)
    ↓
Application Load Balancer
    ↓
EC2 Auto Scaling Group (2-4 instances)
    ↓
RDS PostgreSQL (Multi-AZ)
ElastiCache Redis
S3 (Static files)
```

### Step 1: RDS PostgreSQL

```bash
# Create RDS instance via AWS Console
- Engine: PostgreSQL 15
- Instance: db.t3.medium (2 vCPU, 4GB RAM)
- Storage: 100GB SSD
- Multi-AZ: Yes (for production)
- Backup retention: 7 days
```

### Step 2: ElastiCache Redis

```bash
# Create Redis cluster
- Engine: Redis 7.x
- Node type: cache.t3.micro (start small)
- Number of replicas: 1
```

### Step 3: EC2 Launch Template

```bash
# Create launch template
- AMI: Ubuntu 22.04
- Instance type: t3.medium
- Security group: Allow 80, 443, SSH
- User data script:
```

```bash
#!/bin/bash
apt update && apt upgrade -y
apt install python3.11 python3-pip nginx supervisor -y

# Clone and setup application
cd /var/www
git clone https://github.com/yourusername/examforms.git
cd examforms
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure from S3 (store sensitive config in S3)
aws s3 cp s3://your-bucket/config/.env /var/www/examforms/.env

# Start services
supervisorctl reread
supervisorctl update
```

### Step 4: Auto Scaling Group

```bash
# Create Auto Scaling Group
- Desired capacity: 2
- Minimum: 2
- Maximum: 10
- Target tracking: CPU 70%
- Health check: ELB
```

### Step 5: Application Load Balancer

```bash
# Create ALB
- Scheme: Internet-facing
- Listeners: HTTP (80) → HTTPS (443)
- Target group: EC2 instances
- Health check: /health/
- SSL certificate: ACM certificate
```

### Step 6: CloudFront CDN

```bash
# Create CloudFront distribution
- Origin: ALB DNS
- Cache behavior: Cache based on headers
- Compress: Yes
- Price class: Use only US, Europe, Asia
- Alternate domain: examforms.org
- SSL certificate: ACM certificate
```

---

## CLOUDFLARE SETUP (Recommended)

### Step 1: Add Site to Cloudflare

```bash
# Go to Cloudflare Dashboard
1. Add site: examforms.org
2. Update nameservers at domain registrar
3. Wait for activation (1-24 hours)
```

### Step 2: Configure DNS

```
Type    Name    Content             Proxy
A       @       your_server_ip      Proxied (orange cloud)
A       www     your_server_ip      Proxied
```

### Step 3: SSL/TLS Settings

```bash
# SSL/TLS → Overview
- Encryption mode: Full (strict)

# SSL/TLS → Edge Certificates
- Always Use HTTPS: On
- Minimum TLS Version: 1.2
- Automatic HTTPS Rewrites: On
- Certificate Transparency Monitoring: On
```

### Step 4: Caching Rules

```bash
# Caching → Configuration
- Caching Level: Standard
- Browser Cache TTL: 4 hours

# Page Rules:
1. examforms.org/static/*
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 month

2. examforms.org/*-admit-card
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 hour
```

### Step 5: Performance Optimization

```bash
# Speed → Optimization
- Auto Minify: HTML, CSS, JS (all checked)
- Brotli: On
- Early Hints: On
- Rocket Loader: Off (test first)
- Mirage: On (image optimization)
```

---

## DATABASE MIGRATION

### Initial Migration

```bash
# Activate virtual environment
source venv/bin/activate

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load initial data (if any)
python manage.py loaddata initial_exams.json
```

### Backup Strategy

```bash
# Daily automated backup script
nano /usr/local/bin/backup_db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/examforms"
mkdir -p $BACKUP_DIR

# PostgreSQL backup
PGPASSWORD="your_password" pg_dump -U examforms_user -h localhost examforms > $BACKUP_DIR/examforms_$DATE.sql

# Compress
gzip $BACKUP_DIR/examforms_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/examforms_$DATE.sql.gz s3://your-backup-bucket/database/

# Keep only last 7 days
find $BACKUP_DIR -name "examforms_*.sql.gz" -mtime +7 -delete
```

```bash
# Make executable
chmod +x /usr/local/bin/backup_db.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_db.sh
```

---

## MONITORING SETUP

### 1. Application Monitoring (Sentry)

```python
# In settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

### 2. Server Monitoring (Uptime Robot)

```bash
# Create monitors at uptimerobot.com
- Monitor type: HTTPS
- URL: https://examforms.org
- Monitoring interval: 5 minutes
- Alert contacts: Your email/SMS
```

### 3. Log Management

```bash
# Install Logrotate
nano /etc/logrotate.d/examforms
```

```
/var/log/examforms/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart examforms_web
    endscript
}
```

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] Code reviewed and tested
- [ ] Database migrations prepared
- [ ] Environment variables configured
- [ ] Static files collected
- [ ] SSL certificate ready
- [ ] Backup strategy in place

### Deployment
- [ ] Create backup of current version
- [ ] Pull latest code
- [ ] Run migrations
- [ ] Collect static files
- [ ] Restart application servers
- [ ] Clear cache

### Post-Deployment
- [ ] Check website loads
- [ ] Test critical user flows
- [ ] Check error logs
- [ ] Monitor performance metrics
- [ ] Verify search console
- [ ] Check AdSense

---

## ROLLBACK PROCEDURE

```bash
# If deployment fails:

# 1. Revert code
git checkout <previous-commit-hash>

# 2. Revert database (if needed)
psql -U examforms_user examforms < /var/backups/examforms/examforms_latest.sql

# 3. Restart services
supervisorctl restart all

# 4. Clear cache
redis-cli FLUSHALL

# 5. Verify site is working
curl -I https://examforms.org
```

---

## SCALING CHECKLIST

### When to Scale Up

**Traffic Indicators**:
- CPU usage > 80% consistently
- Memory usage > 85%
- Response time > 2 seconds
- Error rate > 0.1%

**Actions**:
1. Add more web servers (horizontal scaling)
2. Upgrade database (vertical scaling)
3. Add database read replicas
4. Implement caching aggressively
5. Use CDN for all static assets

