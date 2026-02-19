#!/bin/bash

# ExamForms.org - Automated Deployment Script
# Server: 72.62.213.183
# Run this script on your Hostinger VPS

set -e  # Exit on any error

echo "🚀 Starting ExamForms.org Deployment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Update System
echo -e "${GREEN}Step 1: Updating system packages...${NC}"
apt update && apt upgrade -y

# Step 2: Install Dependencies
echo -e "${GREEN}Step 2: Installing dependencies...${NC}"
apt install -y git curl wget vim nano htop ufw \
    python3 python3-pip python3-venv python3-dev \
    build-essential libssl-dev libffi-dev python3-setuptools \
    libpq-dev postgresql postgresql-contrib \
    nginx certbot python3-certbot-nginx

# Step 3: Configure Firewall
echo -e "${GREEN}Step 3: Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Step 4: Setup PostgreSQL
echo -e "${GREEN}Step 4: Setting up PostgreSQL...${NC}"
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS examforms_db;
DROP USER IF EXISTS examforms_user;
CREATE DATABASE examforms_db;
CREATE USER examforms_user WITH PASSWORD 'ExamForms@2026!Secure';
ALTER ROLE examforms_user SET client_encoding TO 'utf8';
ALTER ROLE examforms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE examforms_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE examforms_db TO examforms_user;
EOF

echo -e "${GREEN}Database created successfully!${NC}"

# Step 5: Clone Project
echo -e "${GREEN}Step 5: Cloning project from GitHub...${NC}"
cd /var/www/
if [ -d "examforms" ]; then
    echo -e "${YELLOW}Project directory exists. Removing...${NC}"
    rm -rf examforms
fi
git clone https://github.com/captosoftdigital/examforms.git
cd examforms

# Step 6: Setup Python Environment
echo -e "${GREEN}Step 6: Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary whitenoise python-dotenv

# Step 7: Create Environment File
echo -e "${GREEN}Step 7: Creating environment configuration...${NC}"
cat > /var/www/examforms/.env << 'ENVEOF'
SECRET_KEY=django-insecure-examforms-production-key-change-this-xyz123abc456def
DEBUG=False
ALLOWED_HOSTS=examforms.org,www.examforms.org,72.62.213.183

DB_NAME=examforms_db
DB_USER=examforms_user
DB_PASSWORD=ExamForms@2026!Secure
DB_HOST=localhost
DB_PORT=5432

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
ENVEOF

# Step 8: Run Django Setup
echo -e "${GREEN}Step 8: Running Django migrations...${NC}"
cd /var/www/examforms/src/admin_panel

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (non-interactive)
echo -e "${YELLOW}Creating superuser (admin)...${NC}"
python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@examforms.org', 'Admin@2026!Secure')
    print('Superuser created successfully!')
else:
    print('Superuser already exists!')
PYEOF

# Step 9: Setup Gunicorn
echo -e "${GREEN}Step 9: Configuring Gunicorn...${NC}"

# Create Gunicorn socket
cat > /etc/systemd/system/gunicorn.socket << 'SOCKEOF'
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
SOCKEOF

# Create Gunicorn service
cat > /etc/systemd/system/gunicorn.service << 'SVCEOF'
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
SVCEOF

# Start Gunicorn
systemctl daemon-reload
systemctl start gunicorn.socket
systemctl enable gunicorn.socket

# Step 10: Setup Nginx
echo -e "${GREEN}Step 10: Configuring Nginx...${NC}"

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create Nginx config
cat > /etc/nginx/sites-available/examforms.org << 'NGINXEOF'
server {
    listen 80;
    server_name examforms.org www.examforms.org 72.62.213.183;

    client_max_body_size 100M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
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
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
}
NGINXEOF

# Enable site
ln -sf /etc/nginx/sites-available/examforms.org /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
systemctl enable nginx

# Step 11: Set Permissions
echo -e "${GREEN}Step 11: Setting permissions...${NC}"
chown -R root:www-data /var/www/examforms
chmod -R 755 /var/www/examforms

# Step 12: Final Status Check
echo -e "${GREEN}Step 12: Checking service status...${NC}"
echo ""
echo "=== PostgreSQL Status ==="
systemctl status postgresql --no-pager -l

echo ""
echo "=== Gunicorn Status ==="
systemctl status gunicorn --no-pager -l

echo ""
echo "=== Nginx Status ==="
systemctl status nginx --no-pager -l

# Step 13: Display Results
echo ""
echo "================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo "================================================"
echo ""
echo "🌐 Your website is now accessible at:"
echo "   - http://72.62.213.183"
echo "   - http://examforms.org (after DNS propagates)"
echo ""
echo "🔐 Admin Panel:"
echo "   - URL: http://72.62.213.183/admin/"
echo "   - Username: admin"
echo "   - Password: Admin@2026!Secure"
echo ""
echo "📊 Next Steps:"
echo "   1. Configure DNS A records to point to 72.62.213.183"
echo "   2. Wait 5-30 minutes for DNS propagation"
echo "   3. Install SSL: certbot --nginx -d examforms.org -d www.examforms.org"
echo "   4. Test your website thoroughly"
echo ""
echo "🔍 Useful Commands:"
echo "   - View logs: journalctl -u gunicorn -f"
echo "   - Restart: systemctl restart gunicorn nginx"
echo "   - Status: systemctl status gunicorn nginx"
echo ""
echo "================================================"
