## Platform Requirements & Deployment Checklist

This document describes the software and infrastructure prerequisites for installing and operating the `invproj` platform in two primary environments: Linux (Ubuntu Server with Nginx/Gunicorn) and Windows Server (IIS/uwsgi or Waitress). Each section lists base OS requirements, runtime dependencies, Python packages, database prerequisites, auxiliary services, and optional tooling for development, testing, and observability.

### 1. Common Application Requirements

Regardless of the operating system, the following baseline requirements apply:

- Python 3.11 (recommended) with virtual environment support (`venv`).
- PostgreSQL 15 or later with extensions:
  - `uuid-ossp`
  - `pgcrypto`
  - `btree_gin`
  - `pg_trgm`
- Redis 7.x for caching, Celery task queues, and WebSocket/message brokering (optional but recommended).
- Node.js 18.x LTS (for building frontend assets, if using webpack/Vite).
- Git 2.40+ for code deployment.
- OpenSSL 1.1+ for TLS.
- Time synchronization (NTP) to ensure audit timestamps remain consistent.
- Python packages (requirements file):
  - `Django 4.2`
  - `djangorestframework`
  - `psycopg[binary]`
  - `django-filter`
  - `django-cors-headers`
  - `django-environ`
  - `celery`
  - `redis`
  - `gunicorn` (Linux) / `waitress` or `wfastcgi` (Windows)
  - `whitenoise`
  - `python-dateutil`
  - `pytz`
  - `numpy`, `pandas` (reporting/analytics, optional)
  - `openpyxl` or `xlsxwriter` for exports
  - `reportlab` or `weasyprint` for PDF generation
  - `django-axes` or custom security tooling (optional for login auditing)
- Frontend build dependencies (if bundling static assets): `npm`, `yarn` or `pnpm` plus React/Vue build toolchain if used.
- Logging & monitoring integrations: support for sending logs to syslog, ELK, or Azure Monitor; metrics via Prometheus or Windows Performance Counters.

### 2. Linux Deployment (Ubuntu 22.04 LTS + Nginx + Gunicorn)

#### 2.1 Operating System & Packages
- Ubuntu Server 22.04 LTS (Jammy) with latest security updates.
- Install base packages:
  ```bash
  sudo apt update && sudo apt upgrade
  sudo apt install python3.11 python3.11-venv python3.11-dev \
       build-essential libpq-dev nginx redis-server postgresql postgresql-contrib \
       git curl nodejs npm
  ```
- Optional packages: `certbot` for Let’s Encrypt, `supervisor` or `systemd` unit files for process management, `fail2ban` for hardening.

#### 2.2 Web Server & Application Server
- Nginx 1.18+ as reverse proxy.
- Gunicorn as WSGI server (run inside virtualenv).
- Sample systemd unit for Gunicorn:
  ```ini
  [Unit]
  Description=gunicorn daemon for invproj
  After=network.target

  [Service]
  User=invproj
  Group=www-data
  WorkingDirectory=/opt/invproj
  ExecStart=/opt/invproj/venv/bin/gunicorn config.wsgi:application \
           --bind unix:/run/gunicorn/invproj.sock --workers 4 --timeout 120
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```
- Nginx site configuration (snippet):
  ```nginx
  server {
      listen 80;
      server_name invproj.example.com;

      location = /favicon.ico { access_log off; log_not_found off; }
      location /static/ {
          alias /opt/invproj/static/;
      }
      location /media/ {
          alias /opt/invproj/media/;
      }
      location / {
          include proxy_params;
          proxy_pass http://unix:/run/gunicorn/invproj.sock;
      }
  }
  ```
- Use `certbot --nginx` for HTTPS certificates.

#### 2.3 Database Setup
- PostgreSQL service running locally or on managed instance.
- Create database and user:
  ```sql
  CREATE DATABASE invproj_db WITH ENCODING 'UTF8';
  CREATE USER invproj_user WITH PASSWORD 'STRONG_PASSWORD';
  GRANT ALL PRIVILEGES ON DATABASE invproj_db TO invproj_user;
  ```
- Enable extensions in database:
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  CREATE EXTENSION IF NOT EXISTS "pgcrypto";
  CREATE EXTENSION IF NOT EXISTS "btree_gin";
  CREATE EXTENSION IF NOT EXISTS "pg_trgm";
  ```
- Configure PostgreSQL `postgresql.conf` and `pg_hba.conf` for performance/security.

#### 2.4 Static & Media Assets
- Run `python manage.py collectstatic`.
- Ensure file permissions `www-data:invproj` on static/media directories.
- Consider S3-compatible storage for media if large volume expected.

#### 2.5 Background Tasks & Scheduling
- Celery worker + beat service (systemd or supervisor) connecting to Redis.
- Cron/systemd timers for periodic tasks (cleanup, report generation).

#### 2.6 Monitoring & Logging
- Forward logs via rsyslog or Filebeat to central log store.
- Use Prometheus node exporter, PostgreSQL exporter, and custom application metrics.
- Failover and backup strategy: automated DB backups (pg_dump or wal-g), retention policy, and restore tests.

### 3. Windows Deployment (Windows Server 2022 + IIS)

#### 3.1 Operating System & Packages
- Windows Server 2022 (or 2019) Standard/Datacenter.
- Install roles/features:
  - Web Server (IIS) with CGI/ISAPI support.
  - URL Rewrite Module.
  - WebSockets (if real-time features required).
- Install dependencies:
  - Python 3.11 (64-bit) from python.org.
  - Visual C++ Build Tools / `Build Tools for Visual Studio` for compiling native packages (e.g., `psycopg` wheels may require libs).
  - PostgreSQL 15 Windows installer.
  - Redis (Memurai or Redis for Windows port) if needed on Windows; otherwise use remote Redis instance.
  - Node.js 18.x (Windows installer).
  - Git for Windows.
  - NSSM (Non-Sucking Service Manager) or `Task Scheduler` for service management if not using IIS native worker process.

#### 3.2 IIS + WSGI Configuration
- Options:
  1. **`wfastcgi`** (Microsoft-supported WSGI handler):
     - Install via `pip install wfastcgi`.
     - Run `wfastcgi-enable` to register handler mapping in IIS.
     - Configure site to use the generated `web.config` pointing to Django `wsgi.py`.
  2. **`waitress` + IIS Reverse Proxy`**:
     - Run Waitress as Windows service using NSSM.
     - Configure IIS URL Rewrite to proxy to `http://127.0.0.1:8000`.
- Example `web.config` snippet (wfastcgi):
  ```xml
  <configuration>
    <system.webServer>
      <handlers>
        <add name="Python FastCGI" path="*" verb="*" modules="FastCgiModule"
             scriptProcessor="C:\Python311\python.exe|C:\Python311\Scripts\wfastcgi.py"
             resourceType="Unspecified" requireAccess="Script" />
      </handlers>
      <rewrite>
        <rules>
          <rule name="Static Files" stopProcessing="true">
            <match url="^static/(.*)$" />
            <action type="Rewrite" url="C:\inetpub\wwwroot\invproj\static\{R:1}" />
          </rule>
        </rules>
      </rewrite>
    </system.webServer>
    <appSettings>
      <add key="WSGI_HANDLER" value="config.wsgi.application" />
      <add key="PYTHONPATH" value="C:\inetpub\wwwroot\invproj" />
    </appSettings>
  </configuration>
  ```

#### 3.3 Windows Services & Scheduling
- Use Task Scheduler or NSSM to run Celery workers.
- Use Windows Services for Redis if local.
- For static asset builds, run Node.js build scripts manually or via CI/CD pipelines.

#### 3.4 Security Hardening
- Enable HTTPS via IIS Manager (self-signed for dev, certificate from corporate CA/Let’s Encrypt via win-acme for prod).
- Configure Windows Firewall for allowed ports (80/443, DB, Redis, etc.).
- Enforce NTFS permissions: application pool identity needs read/write to `static/`, `media/`, logs.

### 4. Development Environment Setup
- Recommended OS: Linux/WSL2/Mac for developers, but Windows is possible with the above stack.
- Use Docker Compose as alternative local setup: services for PostgreSQL, Redis, app.
- Provide `.env` template (dotenv) for environment variables.
- Use `pytest` or Django test suite for automated testing; integrate with CI (GitHub Actions, GitLab CI, Azure DevOps).
- Linting/formatting: `flake8`, `black`, `isort`, `pre-commit` hooks.
- Frontend build/test commands (`npm run build`, `npm test`).

### 5. CI/CD & Infrastructure as Code
- Maintain IaC scripts:
  - Terraform/Ansible for provisioning Linux servers.
  - PowerShell DSC or Chocolatey packages for Windows deployment automation.
- CI/CD pipeline steps:
  1. Install dependencies.
  2. Run tests/lint.
  3. Build assets (`collectstatic`, frontend build).
  4. Package release artifact (.tar.gz or zip).
  5. Deploy via SSH (Linux) or WinRM/PowerShell (Windows); restart services.
- Secrets management: use Vault/Azure Key Vault/AWS Secrets Manager or OS-specific key stores.
- Backups: scheduled PostgreSQL dumps, S3/Azure Blob storage, tested restoration scripts.

### 6. Observability & Support Tools
- Monitoring stack:
  - Prometheus + Grafana dashboards (CPU, memory, PostgreSQL metrics, request timings).
  - ELK/EFK stack or Azure Monitor for log aggregation.
  - Sentry or Rollbar for application error tracking.
- Alerting: integrate with Slack/Teams/Email for threshold breaches.
- Health check endpoints: `/healthz` for load balancer probes.
- Disaster recovery playbook: documented RTO/RPO, failover steps, contact lists.

### 7. Optional Integrations & Enhancements
- Message brokers (RabbitMQ) if Celery needs complex routing.
- Elasticsearch/OpenSearch for advanced search features (or leverage PostgreSQL full-text/GiST indexes).
- BI/Reporting: connect to Power BI/Tableau; provide read replicas or data warehouse schema.
- Single Sign-On (SAML/OAuth2) integration via `django-auth-adfs`, `django-allauth`, or corporate IdP.
- Mobile scanner integration using native apps communicating with REST APIs (barcode scanning for warehouses).

This checklist should be reviewed and tailored for each deployment environment. Update it as new dependencies or infrastructure choices (containerization, Kubernetes, cloud services) evolve.
