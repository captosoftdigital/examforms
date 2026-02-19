# 🚀 Hostinger VPS Deployment Guide - ExamForms.org

## Complete Step-by-Step Deployment to Production

**Domain:** examforms.org  
**Server:** Hostinger VPS  
**IP Address:** 72.62.213.183  
**SSH Access:** root@72.62.213.183  
**Password:** RootUser@2025  
**Target:** ₹10 Crore/month Revenue Platform

---

## 📋 Prerequisites

### What You Need
- ✅ Hostinger VPS (Active)
- ✅ Domain: examforms.org (configured)
- ✅ SSH Access: root@72.62.213.183
- ✅ GitHub Repository: https://github.com/captosoftdigital/examforms
- ✅ This deployment guide

### Server Specifications (Recommended)
- **CPU:** 2+ cores
- **RAM:** 4GB+ 
- **Storage:** 50GB+ SSD
- **OS:** Ubuntu 20.04/22.04 LTS
- **Bandwidth:** Unlimited

---

## 🔐 Step 1: Connect to Your VPS

### From Windows (PowerShell/CMD)
```bash
ssh root@72.62.213.183
# Password: RootUser@2025
```

### From Mac/Linux (Terminal)
```bash
ssh root@72.62.213.183
# Password: RootUser@2025
```

### First Time Connection
If you see a fingerprint warning, type `yes` to continue.

---

## 🔧 Step 2: Initial Server Setup

### Update System Packages
```bash
apt update && apt upgrade -y
```

### Install Essential Tools
```bash
apt install -y git curl wget vim nano htop ufw
```

### Set Up Firewall
```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

---

## 🐍 Step 3: Install Python & Dependencies

### Install Python 3.11+
```bash
apt install -y python3 python3-pip python3-venv python3-dev
```

### Verify Installation
```bash
python3 --version
# Should show Python 3.11 or higher
```

### Install Build Dependencies
```bash
apt install -y build-essential libssl-dev libffi-dev python3-setuptools
apt install -y libpq-dev  # For PostgreSQL
```

---

## 🗄️ Step 4: Install & Configure PostgreSQL

### Install PostgreSQL
```bash
apt install -y postgresql postgresql-contrib
```

### Start PostgreSQL Service
```bash
systemctl start postgresql
systemctl enable postgresql
systemctl status postgresql
```

### Create Database & User
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE examforms_db;
CREATE USER examforms_user WITH PASSWORD 'ExamForms@2026!Secure';
ALTER ROLE examforms_user SET client_encoding TO 'utf8';
ALTER ROLE examforms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE examforms_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE examforms_db TO examforms_user;
\q
```

---

## 📦 Step 5: Clone Your Project from GitHub

### Navigate to Web Directory
```bash
cd /var/www/
```

### Clone Repository
```bash
git clone https://github.com/captosoftdigital/examforms.git
cd examforms
```

### Verify Files
```bash
ls -la
# You should see all your project files
```

---

## 🔐 Step 6: Set Up Python Virtual Environment

### Create Virtual Environment
```bash
cd /var/www/examforms
python3 -m venv venv
```

### Activate Virtual Environment
```bash
source venv/bin/activate
```

### Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Install Additional Production Packages
```bash
pip install gunicorn psycopg2-binary whitenoise python-dotenv
```

---

## ⚙️ Step 7: Configure Django for Production

### Create Environment File
```bash
nano /var/www/examforms/.env
```

### Add Configuration (Copy & Paste)
```env
# Django Settings
SECRET_KEY='django-insecure-change-this-to-random-50-char-string-xyz123abc'
DEBUG=False
ALLOWED_HOSTS=examforms.org,www.examforms.org,72.62.213.183

# Database Settings
DB_NAME=examforms_db
DB_USER=examforms_user
DB_PASSWORD=ExamForms@2026!Secure
DB_HOST=localhost
DB_PORT=5432

# Email Settings (Configure later)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## 🗃️ Step 8: Run Database Migrations

### Navigate to Django Project
```bash
cd /var/www/examforms/src/admin_panel
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@examforms.org
# Password: (create a strong password)
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Load Initial Data (Optional)
```bash
cd /var/www/examforms
python seed_database.py
```

---

## 🦄 Step 9: Install & Configure Gunicorn

### Create Gunicorn Socket File
```bash
nano /etc/systemd/system/gunicorn.socket
```

Add:
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

### Create Gunicorn Service File
```bash
nano /etc/systemd/system/gunicorn.service
```

Add:
```ini
[Unit]
Description=gunicorn daemon for ExamForms.org
Requires=gunicorn.socket
After=network.target

[Service]
User=root
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

### Start Gunicorn
```bash
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl status gunicorn.socket
```

### Test Gunicorn Socket
```bash
curl --unix-socket /run/gunicorn.sock localhost
```

---

## 🌐 Step 10: Install & Configure Nginx

### Install Nginx
```bash
apt install -y nginx
```

### Create Nginx Configuration
```bash
nano /etc/nginx/sites-available/examforms.org
```

Add:
```nginx
server {
    listen 80;
    server_name examforms.org www.examforms.org 72.62.213.183;

    client_max_body_size 100M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/examforms/src/admin_panel/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/examforms/src/admin_panel/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
}
```

### Enable Site
```bash
ln -s /etc/nginx/sites-available/examforms.org /etc/nginx/sites-enabled/
```

### Test Nginx Configuration
```bash
nginx -t
```

### Restart Nginx
```bash
systemctl restart nginx
systemctl enable nginx
systemctl status nginx
```

---

## 🔒 Step 11: Install SSL Certificate (HTTPS)

### Install Certbot
```bash
apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate
```bash
certbot --nginx -d examforms.org -d www.examforms.org
```

Follow the prompts:
- Enter email: your-email@example.com
- Agree to terms: Y
- Share email: N (optional)
- Redirect HTTP to HTTPS: 2 (Yes)

### Test Auto-Renewal
```bash
certbot renew --dry-run
```

---

## 🎯 Step 12: Configure Domain DNS

### In Your Domain Registrar (Hostinger/GoDaddy/etc.)

Add these DNS records:

**A Record:**
```
Type: A
Name: @
Value: 72.62.213.183
TTL: 3600
```

**A Record (www):**
```
Type: A
Name: www
Value: 72.62.213.183
TTL: 3600
```

**Wait 5-30 minutes for DNS propagation**

---

## ✅ Step 13: Final Verification

### Check Services Status
```bash
systemctl status gunicorn
systemctl status nginx
systemctl status postgresql
```

### Test Website
```bash
# Test HTTP (should redirect to HTTPS)
curl -I http://examforms.org

# Test HTTPS
curl -I https://examforms.org
```

### Visit in Browser
- https://examforms.org
- https://www.examforms.org
- https://examforms.org/admin/

---

## 🔄 Step 14: Deploy Updates (Future)

### When You Push New Code to GitHub

```bash
# SSH into server
ssh root@72.62.213.183
# Password: RootUser@2025

# Navigate to project
cd /var/www/examforms

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Run migrations
cd src/admin_panel
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn
systemctl restart gunicorn

# Restart Nginx (if needed)
systemctl restart nginx

# Check status
systemctl status gunicorn
```

---

## 📊 Step 15: Monitoring & Maintenance

### View Logs
```bash
# Gunicorn logs
journalctl -u gunicorn -f

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

### Monitor Server Resources
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Check running processes
ps aux | grep gunicorn
ps aux | grep nginx
```

### Database Backup
```bash
# Create backup directory
mkdir -p /backups

# Create backup
pg_dump -U examforms_user examforms_db > /backups/examforms_$(date +%Y%m%d).sql

# Restore backup
psql -U examforms_user examforms_db < /backups/examforms_20260219.sql
```

---

## 🚨 Troubleshooting

### Issue: Website Not Loading

**Check Nginx:**
```bash
systemctl status nginx
nginx -t
```

**Check Gunicorn:**
```bash
systemctl status gunicorn
journalctl -u gunicorn -n 50
```

**Check Firewall:**
```bash
ufw status
```

### Issue: 502 Bad Gateway

**Restart Services:**
```bash
systemctl restart gunicorn
systemctl restart nginx
```

**Check Socket:**
```bash
ls -la /run/gunicorn.sock
```

### Issue: Static Files Not Loading

**Collect Static Files:**
```bash
cd /var/www/examforms/src/admin_panel
python manage.py collectstatic --noinput
```

**Check Permissions:**
```bash
chmod -R 755 /var/www/examforms/src/admin_panel/staticfiles/
```

### Issue: Database Connection Error

**Check PostgreSQL:**
```bash
systemctl status postgresql
sudo -u postgres psql -c "SELECT 1"
```

**Test Connection:**
```bash
psql -U examforms_user -d examforms_db -h localhost
```

---

## 🔐 Security Best Practices

### 1. Change Default SSH Port (Optional)
```bash
nano /etc/ssh/sshd_config
# Change Port 22 to Port 2222
systemctl restart sshd
ufw allow 2222/tcp
```

### 2. Set Up Fail2Ban
```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. Regular Updates
```bash
# Set up automatic security updates
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## ✅ Deployment Checklist

- [ ] SSH connection successful (root@72.62.213.183)
- [ ] System packages updated
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] Python 3.11+ installed
- [ ] PostgreSQL installed and configured
- [ ] Database created (examforms_db)
- [ ] Project cloned from GitHub
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] Static files collected
- [ ] Gunicorn configured and running
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] DNS records configured
- [ ] Website accessible via HTTPS
- [ ] Admin panel accessible
- [ ] All features working correctly

---

## 🎉 Success!

Your **award-winning ExamForms.org** is now live on production!

**Access Your Website:**
- 🌐 **Public Site:** https://examforms.org
- 🔐 **Admin Panel:** https://examforms.org/admin/
- 📊 **Server IP:** 72.62.213.183
- 🔑 **SSH:** root@72.62.213.183 (Password: RootUser@2025)

**Next Steps:**
1. Test all features thoroughly
2. Set up monitoring (Google Analytics, etc.)
3. Configure email notifications
4. Set up automated backups
5. Monitor performance and optimize
6. Start marketing and SEO campaigns
7. Achieve ₹10 Crore/month revenue! 🚀

---

**🎯 Your Multi-Billion Dollar Platform is LIVE! 💎**

*Deployment Guide Version: 2.0*  
*Last Updated: February 19, 2026*  
*Status: Production Ready ✅*
