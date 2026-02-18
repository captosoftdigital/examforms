# ExamForms.org - Hostinger Deployment Checklist

## Pre-Deployment
- [ ] Code pushed to GitHub: https://github.com/captosoftdigital/examforms ✅
- [ ] Hostinger VPS/hosting plan active
- [ ] Domain examforms.org registered
- [ ] SSH access to server enabled

## Server Setup (30-45 minutes)
- [ ] Connect via SSH
- [ ] Update system packages
- [ ] Install Python 3.11
- [ ] Install PostgreSQL
- [ ] Install Redis
- [ ] Install Nginx
- [ ] Create database and user
- [ ] Configure firewall (UFW)

## Application Setup (20-30 minutes)
- [ ] Clone repository from GitHub
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Install Playwright browsers
- [ ] Create and configure .env file
- [ ] Generate Django SECRET_KEY
- [ ] Run database migrations
- [ ] Create Django superuser
- [ ] Collect static files
- [ ] Test Django application

## Production Configuration (15-20 minutes)
- [ ] Configure Gunicorn service
- [ ] Configure Nginx
- [ ] Start and enable services
- [ ] Test application via HTTP

## Domain & SSL (10-15 minutes)
- [ ] Point domain DNS to server IP
- [ ] Wait for DNS propagation (5-30 min)
- [ ] Install Certbot
- [ ] Obtain SSL certificate
- [ ] Test HTTPS access
- [ ] Verify auto-renewal

## Background Tasks (10 minutes)
- [ ] Configure Celery worker service
- [ ] Configure Celery beat service
- [ ] Start and enable Celery services
- [ ] Verify Celery is running

## Monitoring & Maintenance (15 minutes)
- [ ] Setup log rotation
- [ ] Create backup script
- [ ] Schedule daily backups (cron)
- [ ] Install fail2ban (optional)
- [ ] Configure monitoring tools

## Final Verification
- [ ] Visit https://examforms.org
- [ ] Login to admin panel
- [ ] Check all services running
- [ ] Test database connection
- [ ] Verify static files loading
- [ ] Check SSL certificate valid
- [ ] Test scraper functionality

## Post-Deployment
- [ ] Add Google AdSense code
- [ ] Submit sitemap to Google Search Console
- [ ] Setup Google Analytics
- [ ] Configure Sentry for error tracking
- [ ] Setup UptimeRobot monitoring
- [ ] Document admin credentials (secure location)

---

## Quick Commands Reference

### Check All Services
```bash
sudo systemctl status gunicorn nginx celery celerybeat postgresql redis
```

### Restart All Services
```bash
sudo systemctl restart gunicorn nginx celery celerybeat
```

### View Logs
```bash
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

### Update Application
```bash
cd /var/www/examforms
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd src/admin_panel
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn celery celerybeat
```

---

## Estimated Total Time: 2-3 hours

**Note**: Most time is spent waiting for installations and DNS propagation.
