# Deployment Guide

Complete guide for deploying the invproj platform to production environments.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Server Setup](#2-server-setup)
3. [Application Deployment](#3-application-deployment)
4. [Database Configuration](#4-database-configuration)
5. [Web Server Configuration](#5-web-server-configuration)
6. [SSL/TLS Setup](#6-ssltls-setup)
7. [Static Files](#7-static-files)
8. [Environment Variables](#8-environment-variables)
9. [Security Checklist](#9-security-checklist)
10. [Monitoring & Logging](#10-monitoring--logging)
11. [Backup Strategy](#11-backup-strategy)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

### 1.1 System Requirements

- **Operating System**: Ubuntu 22.04 LTS or later (recommended)
- **Python**: 3.12 or later
- **Database**: PostgreSQL 14 or later
- **Web Server**: Nginx 1.18 or later
- **Application Server**: Gunicorn or uWSGI
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Disk Space**: Minimum 20GB (50GB+ recommended for production)

### 1.2 Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y python3.12 python3.12-venv python3.12-dev \
    build-essential libpq-dev

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
sudo apt install -y nginx

# Install Git (if not already installed)
sudo apt install -y git

# Install Supervisor (for process management)
sudo apt install -y supervisor
```

---

## 2. Server Setup

### 2.1 Create Application User

```bash
# Create dedicated user for application
sudo adduser --system --group --home /var/www/invproj invproj

# Add user to www-data group (for Nginx access)
sudo usermod -a -G www-data invproj
```

### 2.2 Create Application Directory

```bash
# Create application directory
sudo mkdir -p /var/www/invproj
sudo chown invproj:invproj /var/www/invproj

# Clone repository (or copy files)
cd /var/www/invproj
sudo -u invproj git clone <repository-url> .

# Or copy files manually
# sudo cp -r /path/to/invproj/* /var/www/invproj/
# sudo chown -R invproj:invproj /var/www/invproj
```

---

## 3. Application Deployment

### 3.1 Python Virtual Environment

```bash
cd /var/www/invproj

# Create virtual environment
sudo -u invproj python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Environment Configuration

```bash
# Copy environment template
sudo -u invproj cp env.sample .env

# Edit environment file
sudo -u invproj nano .env
```

**Required Environment Variables**:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,192.168.1.100
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DJANGO_TIME_ZONE=Asia/Tehran

# Database
DATABASE_URL=postgresql://invproj_user:your_password@localhost:5432/invproj_db

# Security (for production)
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

**Generate Secret Key**:
```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3.3 Database Migrations

```bash
# Activate virtual environment
source .venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Compile translations
python manage.py compilemessages
```

---

## 4. Database Configuration

### 4.1 PostgreSQL Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE invproj_db;
CREATE USER invproj_user WITH PASSWORD 'your_secure_password';
ALTER ROLE invproj_user SET client_encoding TO 'utf8';
ALTER ROLE invproj_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE invproj_user SET timezone TO 'Asia/Tehran';
GRANT ALL PRIVILEGES ON DATABASE invproj_db TO invproj_user;
\q
```

### 4.2 PostgreSQL Configuration

Edit `/etc/postgresql/14/main/postgresql.conf`:

```conf
# Performance tuning (adjust based on server resources)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:

```conf
# Allow local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## 5. Web Server Configuration

### 5.1 Gunicorn Setup

Create Gunicorn configuration file `/var/www/invproj/gunicorn_config.py`:

```python
# Gunicorn configuration file
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "/var/log/invproj/gunicorn_access.log"
errorlog = "/var/log/invproj/gunicorn_error.log"
loglevel = "info"
```

### 5.2 Supervisor Configuration

Create Supervisor configuration `/etc/supervisor/conf.d/invproj.conf`:

```ini
[program:invproj]
command=/var/www/invproj/.venv/bin/gunicorn config.wsgi:application --config /var/www/invproj/gunicorn_config.py
directory=/var/www/invproj
user=invproj
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/invproj/gunicorn.log
environment=PATH="/var/www/invproj/.venv/bin"
```

Create log directory:
```bash
sudo mkdir -p /var/log/invproj
sudo chown invproj:invproj /var/log/invproj
```

Start Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start invproj
sudo supervisorctl status invproj
```

### 5.3 Nginx Configuration

Create Nginx configuration `/etc/nginx/sites-available/invproj`:

```nginx
upstream invproj {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (see SSL/TLS Setup section)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Logging
    access_log /var/log/nginx/invproj_access.log;
    error_log /var/log/nginx/invproj_error.log;
    
    # Client body size (for file uploads)
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /var/www/invproj/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files (if needed)
    location /media/ {
        alias /var/www/invproj/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Application
    location / {
        proxy_pass http://invproj;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/invproj /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 6. SSL/TLS Setup

### 6.1 Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### 6.2 Self-Signed Certificate (Development Only)

```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/invproj.key \
    -out /etc/ssl/certs/invproj.crt
```

---

## 7. Static Files

### 7.1 Collect Static Files

```bash
cd /var/www/invproj
source .venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput

# Verify
ls -la /var/www/invproj/staticfiles/
```

### 7.2 Static Files Permissions

```bash
sudo chown -R invproj:www-data /var/www/invproj/staticfiles/
sudo chmod -R 755 /var/www/invproj/staticfiles/
```

---

## 8. Environment Variables

### 8.1 Production Environment File

Ensure `.env` file has production settings:

```bash
# Security
DJANGO_SECRET_KEY=<strong-random-secret-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database
DATABASE_URL=postgresql://invproj_user:password@localhost:5432/invproj_db

# Timezone
DJANGO_TIME_ZONE=Asia/Tehran

# Email (if configured)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 8.2 File Permissions

```bash
# Secure .env file
sudo chmod 600 /var/www/invproj/.env
sudo chown invproj:invproj /var/www/invproj/.env
```

---

## 9. Security Checklist

### 9.1 Django Settings

- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is strong and unique
- [ ] `ALLOWED_HOSTS` includes domain
- [ ] `CSRF_TRUSTED_ORIGINS` configured
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_BROWSER_XSS_FILTER = True`
- [ ] `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [ ] `X_FRAME_OPTIONS = 'DENY'`

### 9.2 Server Security

- [ ] Firewall configured (UFW)
- [ ] SSH key authentication only
- [ ] Regular security updates
- [ ] Fail2ban installed
- [ ] Database user has minimal privileges
- [ ] Application user has minimal privileges

### 9.3 Firewall Configuration

```bash
# Install UFW
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

---

## 10. Monitoring & Logging

### 10.1 Log Rotation

Create logrotate configuration `/etc/logrotate.d/invproj`:

```
/var/log/invproj/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 invproj invproj
    sharedscripts
    postrotate
        supervisorctl restart invproj > /dev/null 2>&1 || true
    endscript
}
```

### 10.2 Application Monitoring

Consider installing:
- **Sentry**: Error tracking
- **Prometheus + Grafana**: Metrics and monitoring
- **New Relic / Datadog**: APM (Application Performance Monitoring)

### 10.3 Health Check Endpoint

Create a simple health check view (optional):

```python
# config/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)
```

---

## 11. Backup Strategy

### 11.1 Database Backup

Create backup script `/usr/local/bin/invproj_backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/invproj"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="invproj_db"
DB_USER="invproj_user"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/invproj_backup.sh
```

### 11.2 Automated Backups

Add to crontab:
```bash
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /usr/local/bin/invproj_backup.sh
```

### 11.3 Media Files Backup

```bash
# Backup media directory
tar -czf /var/backups/invproj/media_$(date +%Y%m%d).tar.gz /var/www/invproj/media/
```

---

## 12. Troubleshooting

### 12.1 Common Issues

#### Issue: 502 Bad Gateway

**Solution**:
```bash
# Check Gunicorn status
sudo supervisorctl status invproj

# Check logs
sudo tail -f /var/log/invproj/gunicorn_error.log

# Restart Gunicorn
sudo supervisorctl restart invproj
```

#### Issue: Static files not loading

**Solution**:
```bash
# Recollect static files
cd /var/www/invproj
source .venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R invproj:www-data /var/www/invproj/staticfiles/
```

#### Issue: Database connection error

**Solution**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U invproj_user -d invproj_db -h localhost

# Check .env file
cat /var/www/invproj/.env | grep DATABASE_URL
```

#### Issue: Permission denied errors

**Solution**:
```bash
# Fix ownership
sudo chown -R invproj:invproj /var/www/invproj

# Fix permissions
sudo chmod -R 755 /var/www/invproj
sudo chmod 600 /var/www/invproj/.env
```

### 12.2 Log Locations

- **Application logs**: `/var/log/invproj/gunicorn_error.log`
- **Nginx access logs**: `/var/log/nginx/invproj_access.log`
- **Nginx error logs**: `/var/log/nginx/invproj_error.log`
- **Supervisor logs**: `/var/log/supervisor/supervisord.log`
- **PostgreSQL logs**: `/var/log/postgresql/postgresql-14-main.log`

### 12.3 Performance Tuning

#### Database Optimization

```sql
-- Analyze tables
ANALYZE;

-- Create indexes (if missing)
CREATE INDEX IF NOT EXISTS idx_item_company ON inventory_item(company_id);
CREATE INDEX IF NOT EXISTS idx_receipt_company ON inventory_receiptpermanent(company_id);
```

#### Gunicorn Workers

Adjust workers based on CPU cores:
```python
# gunicorn_config.py
workers = (2 * CPU_CORES) + 1
```

---

## 13. Deployment Checklist

### Pre-Deployment

- [ ] Server provisioned and configured
- [ ] PostgreSQL installed and configured
- [ ] Application code deployed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Database created and migrations run
- [ ] Superuser created
- [ ] Static files collected

### Deployment

- [ ] Gunicorn configured and running
- [ ] Supervisor configured
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Logging configured
- [ ] Backup script created

### Post-Deployment

- [ ] Application accessible via HTTPS
- [ ] Static files loading correctly
- [ ] Database connections working
- [ ] User login working
- [ ] All features tested
- [ ] Monitoring configured
- [ ] Backups running

---

## 14. Quick Reference

### Useful Commands

```bash
# Restart application
sudo supervisorctl restart invproj

# Restart Nginx
sudo systemctl restart nginx

# Restart PostgreSQL
sudo systemctl restart postgresql

# View application logs
sudo tail -f /var/log/invproj/gunicorn_error.log

# View Nginx logs
sudo tail -f /var/log/nginx/invproj_error.log

# Run migrations
cd /var/www/invproj && source .venv/bin/activate && python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

---

**Last Updated**: 2025-11-21

