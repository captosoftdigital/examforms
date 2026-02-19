# ⚡ Quick Deployment Commands - ExamForms.org

## SSH Connection
```bash
ssh root@72.62.213.183
# Password: RootUser@2025
```

---

## Initial Setup (Run Once)

```bash
# Update system
apt update && apt upgrade -y

# Install essentials
apt install -y git curl wget vim nano htop ufw python3 python3-pip python3-venv python3-dev build-essential libpq-dev postgresql postgresql-contrib nginx certbot python3-certbot-nginx

# Configure firewall
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable

# Create database
sudo -u postgres psql -c "CREATE DATABASE examforms_db;"
sudo -u postgres psql -c "CREATE USER examforms_user WITH PASSWORD 'ExamForms@2026!Secure';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE examforms_db TO examforms_user;"

# Clone project
cd /var/www/
git clone https://github.com/captosoftdigital/examforms.git
cd examforms

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary whitenoise python-dotenv

# Run migrations
cd src/admin_panel
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# Start services
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl restart nginx
systemctl enable nginx

# Get SSL certificate
certbot --nginx -d examforms.org -d www.examforms.org
```

---

## Deploy Updates (Run After Git Push)

```bash
# Connect to server
ssh root@72.62.213.183

# Navigate to project
cd /var/www/examforms

# Pull latest code
git pull origin main

# Activate environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Run migrations
cd src/admin_panel
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
systemctl restart gunicorn
systemctl restart nginx

# Check status
systemctl status gunicorn
systemctl status nginx
```

---

## Useful Commands

### Check Service Status
```bash
systemctl status gunicorn
systemctl status nginx
systemctl status postgresql
```

### View Logs
```bash
# Gunicorn logs
journalctl -u gunicorn -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
systemctl restart gunicorn
systemctl restart nginx
systemctl restart postgresql
```

### Database Backup
```bash
# Backup
pg_dump -U examforms_user examforms_db > /backups/examforms_$(date +%Y%m%d).sql

# Restore
psql -U examforms_user examforms_db < /backups/examforms_20260219.sql
```

### Monitor Resources
```bash
htop           # CPU/Memory
df -h          # Disk space
free -h        # Memory usage
```

---

## Quick Fixes

### 502 Bad Gateway
```bash
systemctl restart gunicorn
systemctl restart nginx
```

### Static Files Not Loading
```bash
cd /var/www/examforms/src/admin_panel
python manage.py collectstatic --noinput
chmod -R 755 staticfiles/
systemctl restart nginx
```

### Database Connection Error
```bash
systemctl restart postgresql
sudo -u postgres psql -c "SELECT 1"
```

---

## Important Paths

- **Project:** `/var/www/examforms/`
- **Virtual Env:** `/var/www/examforms/venv/`
- **Django:** `/var/www/examforms/src/admin_panel/`
- **Static Files:** `/var/www/examforms/src/admin_panel/staticfiles/`
- **Nginx Config:** `/etc/nginx/sites-available/examforms.org`
- **Gunicorn Service:** `/etc/systemd/system/gunicorn.service`
- **Environment:** `/var/www/examforms/.env`

---

## Access URLs

- **Website:** https://examforms.org
- **Admin:** https://examforms.org/admin/
- **Server IP:** 72.62.213.183

---

**🚀 Quick Reference for Fast Deployments!**
