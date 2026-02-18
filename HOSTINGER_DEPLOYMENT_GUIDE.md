# Hostinger Deployment Guide - ExamForms.org

## Prerequisites
- Hostinger VPS or Business/Cloud hosting plan
- Domain: examforms.org (pointed to Hostinger)
- SSH access enabled
- Root or sudo access

---

## Part 1: Initial Server Setup

### Step 1: Connect to Your Hostinger Server

```bash
# Get SSH credentials from Hostinger panel
# Go to: Hostinger Panel → VPS → SSH Access
ssh root@your_server_ip
# Or if using hPanel:
ssh u123456789@your_server_ip
```

### Step 2: Update System

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget vim software-properties-common
```

### Step 3: Install Python 3.11

```bash
# Add deadsnakes PPA for Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11 and dependencies
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify installation
python3.11 --version
```

### Step 4: Install PostgreSQL

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```


### Step 5: Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Run these commands in PostgreSQL prompt:
CREATE DATABASE examforms;
CREATE USER examforms_user WITH PASSWORD 'YourSecurePassword123!';
ALTER ROLE examforms_user SET client_encoding TO 'utf8';
ALTER ROLE examforms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE examforms_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE examforms TO examforms_user;
\q
```

### Step 6: Install Redis

```bash
# Install Redis
sudo apt install -y redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

### Step 7: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## Part 2: Application Setup

### Step 8: Clone Your Repository

```bash
# Create application directory
sudo mkdir -p /var/www/examforms
sudo chown -R $USER:$USER /var/www/examforms
cd /var/www/examforms

# Clone from GitHub
git clone https://github.com/captosoftdigital/examforms.git .
```


### Step 9: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 10: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Gunicorn (production WSGI server)
pip install gunicorn

# Install Playwright browsers (for scraping)
playwright install
playwright install-deps
```

### Step 11: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

**Edit .env with these values:**

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=examforms
DB_USER=examforms_user
DB_PASSWORD=YourSecurePassword123!

# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-generate-random-50-chars
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=examforms.org,www.examforms.org,your_server_ip

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Base URL
BASE_URL=https://examforms.org

# Google AdSense (add later)
ADSENSE_CLIENT_ID=ca-pub-xxxxxxxxxxxxxxxxx
```

**Generate Django Secret Key:**
```bash
python3.11 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```


### Step 12: Run Django Migrations

```bash
# Navigate to Django project
cd /var/www/examforms/src/admin_panel

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin account

# Collect static files
python manage.py collectstatic --noinput
```

### Step 13: Test Django Application

```bash
# Test if Django runs
python manage.py runserver 0.0.0.0:8000

# Open another terminal and test:
curl http://localhost:8000
# Press Ctrl+C to stop the test server
```

---

## Part 3: Configure Gunicorn

### Step 14: Create Gunicorn Configuration

```bash
# Create Gunicorn config directory
sudo mkdir -p /etc/gunicorn

# Create socket file
sudo nano /etc/systemd/system/gunicorn.socket
```

**Add this content:**

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

### Step 15: Create Gunicorn Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**Add this content:**

```ini
[Unit]
Description=gunicorn daemon for ExamForms
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/examforms/src/admin_panel
Environment="PATH=/var/www/examforms/venv/bin"
ExecStart=/var/www/examforms/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          admin_panel.wsgi:application

[Install]
WantedBy=multi-user.target
```


### Step 16: Start Gunicorn

```bash
# Set correct permissions
sudo chown -R www-data:www-data /var/www/examforms

# Start and enable Gunicorn socket
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# Check status
sudo systemctl status gunicorn.socket

# Test socket activation
curl --unix-socket /run/gunicorn.sock localhost
```

---

## Part 4: Configure Nginx

### Step 17: Create Nginx Configuration

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/examforms
```

**Add this configuration:**

```nginx
server {
    listen 80;
    server_name examforms.org www.examforms.org;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/examforms/src/admin_panel/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/examforms/media/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

### Step 18: Enable Nginx Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/examforms /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```


---

## Part 5: Domain Configuration

### Step 19: Point Domain to Server

**In Hostinger Domain Panel:**

1. Go to Hostinger Dashboard → Domains → examforms.org
2. Click "DNS / Nameservers"
3. Add/Update these DNS records:

```
Type    Name    Value                   TTL
A       @       your_server_ip          14400
A       www     your_server_ip          14400
```

4. Wait 5-30 minutes for DNS propagation

### Step 20: Verify Domain

```bash
# Check if domain points to your server
ping examforms.org

# Test HTTP access
curl -I http://examforms.org
```

---

## Part 6: SSL Certificate (HTTPS)

### Step 21: Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### Step 22: Obtain SSL Certificate

```bash
# Get SSL certificate
sudo certbot --nginx -d examforms.org -d www.examforms.org

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect HTTP to HTTPS (option 2)
```

### Step 23: Test SSL Auto-Renewal

```bash
# Test renewal process
sudo certbot renew --dry-run

# Certificate will auto-renew before expiration
```

### Step 24: Verify HTTPS

```bash
# Test HTTPS
curl -I https://examforms.org
```

Visit: https://examforms.org in your browser!


---

## Part 7: Setup Celery for Background Tasks

### Step 25: Create Celery Service

```bash
# Create Celery worker service
sudo nano /etc/systemd/system/celery.service
```

**Add this content:**

```ini
[Unit]
Description=Celery Service for ExamForms
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/examforms/src/admin_panel
Environment="PATH=/var/www/examforms/venv/bin"
ExecStart=/var/www/examforms/venv/bin/celery -A admin_panel worker --loglevel=info --detach

[Install]
WantedBy=multi-user.target
```

### Step 26: Create Celery Beat Service

```bash
sudo nano /etc/systemd/system/celerybeat.service
```

**Add this content:**

```ini
[Unit]
Description=Celery Beat Service for ExamForms
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/examforms/src/admin_panel
Environment="PATH=/var/www/examforms/venv/bin"
ExecStart=/var/www/examforms/venv/bin/celery -A admin_panel beat --loglevel=info

[Install]
WantedBy=multi-user.target
```

### Step 27: Start Celery Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start and enable Celery worker
sudo systemctl start celery
sudo systemctl enable celery

# Start and enable Celery beat
sudo systemctl start celerybeat
sudo systemctl enable celerybeat

# Check status
sudo systemctl status celery
sudo systemctl status celerybeat
```


---

## Part 8: Monitoring & Maintenance

### Step 28: Setup Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/examforms
```

**Add this content:**

```
/var/www/examforms/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
```

### Step 29: Create Backup Script

```bash
# Create backup directory
sudo mkdir -p /var/backups/examforms

# Create backup script
sudo nano /usr/local/bin/backup_examforms.sh
```

**Add this content:**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/examforms"

# Backup database
sudo -u postgres pg_dump examforms > $BACKUP_DIR/db_$DATE.sql
gzip $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/examforms/media/

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup_examforms.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add this line:
0 2 * * * /usr/local/bin/backup_examforms.sh
```


### Step 30: Setup Firewall

```bash
# Install UFW (if not installed)
sudo apt install -y ufw

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## Part 9: Useful Commands

### Service Management

```bash
# Restart all services
sudo systemctl restart gunicorn nginx celery celerybeat

# Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status celery
sudo systemctl status celerybeat

# View logs
sudo journalctl -u gunicorn -f
sudo journalctl -u celery -f
sudo tail -f /var/log/nginx/error.log
```

### Django Management

```bash
# Activate virtual environment
cd /var/www/examforms
source venv/bin/activate

# Run migrations
cd src/admin_panel
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Django shell
python manage.py shell
```

### Update Application

```bash
# Pull latest code
cd /var/www/examforms
git pull origin main

# Activate venv and update
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
cd src/admin_panel
python manage.py migrate
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn celery celerybeat
```


---

## Part 10: Troubleshooting

### Issue: Gunicorn won't start

```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Check socket
sudo systemctl status gunicorn.socket

# Test manually
cd /var/www/examforms/src/admin_panel
source /var/www/examforms/venv/bin/activate
gunicorn --bind 0.0.0.0:8000 admin_panel.wsgi:application
```

### Issue: Nginx 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo systemctl status gunicorn

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Check socket permissions
ls -l /run/gunicorn.sock
```

### Issue: Static files not loading

```bash
# Collect static files again
cd /var/www/examforms/src/admin_panel
source /var/www/examforms/venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/examforms/src/admin_panel/staticfiles/
```

### Issue: Database connection error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test database connection
sudo -u postgres psql -d examforms -c "SELECT 1;"

# Check .env file has correct credentials
cat /var/www/examforms/.env | grep DB_
```

### Issue: Domain not resolving

```bash
# Check DNS propagation
nslookup examforms.org
dig examforms.org

# Check Nginx configuration
sudo nginx -t

# Check if port 80/443 are open
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```


---

## Part 11: Performance Optimization

### Enable Gzip Compression

```bash
sudo nano /etc/nginx/nginx.conf
```

**Add inside http block:**

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
```

### Setup Redis Caching

```bash
# Install Redis Python client (already in requirements.txt)
# Configure in Django settings.py
```

### Monitor Server Resources

```bash
# Install htop
sudo apt install -y htop

# Monitor in real-time
htop

# Check disk usage
df -h

# Check memory usage
free -h
```

---

## Part 12: Security Checklist

- [x] Firewall enabled (UFW)
- [x] SSL certificate installed (HTTPS)
- [x] Debug mode disabled (DEBUG=False)
- [x] Strong database password
- [x] Django SECRET_KEY is random and secure
- [x] Regular backups configured
- [ ] Setup fail2ban for SSH protection
- [ ] Configure security headers in Nginx
- [ ] Setup monitoring (Sentry, UptimeRobot)

### Install Fail2Ban (Optional but Recommended)

```bash
# Install fail2ban
sudo apt install -y fail2ban

# Start and enable
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

---

## Deployment Complete! 🎉

Your ExamForms.org application should now be live at:
- **HTTP**: http://examforms.org (redirects to HTTPS)
- **HTTPS**: https://examforms.org
- **Admin Panel**: https://examforms.org/admin/

### Next Steps:

1. **Test the website** - Visit https://examforms.org
2. **Login to admin** - https://examforms.org/admin/
3. **Configure Google AdSense** - Add your AdSense code
4. **Setup monitoring** - Configure Sentry, UptimeRobot
5. **Start scrapers** - Begin collecting exam data
6. **SEO optimization** - Submit sitemap to Google Search Console

### Support Resources:

- Hostinger Support: https://www.hostinger.com/tutorials
- Django Documentation: https://docs.djangoproject.com/
- Your GitHub Repo: https://github.com/captosoftdigital/examforms

---

**Need Help?** Check the Troubleshooting section or contact Hostinger support.
