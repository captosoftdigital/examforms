# Requirements Document: Hostinger Deployment for ExamForms.org

## Introduction

This document specifies the requirements for deploying the ExamForms.org Django application to Hostinger hosting infrastructure with the domain examforms.org. The deployment must support a production-ready Django 4.2.7 application with Scrapy web scrapers, Celery task scheduling, PostgreSQL database, and Redis caching. The system must handle automated exam information scraping, content generation, and serve a public-facing website with an administrative panel.

## Glossary

- **Deployment_System**: The complete infrastructure and processes for deploying ExamForms.org to Hostinger
- **Django_Application**: The ExamForms.org web application built with Django 4.2.7
- **Hostinger_Environment**: The hosting infrastructure provided by Hostinger (VPS or Cloud Hosting)
- **Web_Server**: The HTTP server (Nginx or Apache) that serves the application
- **Application_Server**: The WSGI server (Gunicorn or uWSGI) that runs the Django application
- **Process_Manager**: The system (Supervisor or systemd) that manages application processes
- **Database_Server**: The PostgreSQL database server
- **Cache_Server**: The Redis server for caching and Celery message broker
- **Task_Worker**: The Celery worker process that executes background tasks
- **Task_Scheduler**: The Celery Beat process that schedules periodic scraping tasks
- **SSL_Certificate**: The TLS/SSL certificate for HTTPS encryption
- **Static_Files**: CSS, JavaScript, and image files served by the web server
- **Media_Files**: User-uploaded or generated files stored on the server
- **Environment_Variables**: Configuration values stored securely outside the codebase
- **Scraper_Process**: The Scrapy-based web scraping processes for exam information
- **Deployment_User**: The system user account that runs the application processes

## Requirements

### Requirement 1: Hostinger Infrastructure Setup

**User Story:** As a system administrator, I want to provision and configure the Hostinger hosting environment, so that the server has the necessary resources and access for deployment.

#### Acceptance Criteria

1. THE Deployment_System SHALL provision a Hostinger VPS or Cloud Hosting instance with minimum 4GB RAM and 2 CPU cores
2. THE Deployment_System SHALL configure SSH access with key-based authentication for secure remote access
3. THE Deployment_System SHALL install Ubuntu 22.04 LTS or later as the operating system
4. THE Deployment_System SHALL configure firewall rules to allow HTTP (port 80), HTTPS (port 443), and SSH (port 22) traffic
5. THE Deployment_System SHALL disable root SSH login and create a dedicated Deployment_User with sudo privileges
6. THE Deployment_System SHALL configure automatic security updates for the operating system
7. THE Deployment_System SHALL allocate minimum 80GB SSD storage for application, database, and logs

### Requirement 2: Domain and DNS Configuration

**User Story:** As a system administrator, I want to configure the examforms.org domain to point to the Hostinger server, so that users can access the application via the domain name.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure DNS A records for examforms.org and www.examforms.org pointing to the server IP address
2. THE Deployment_System SHALL verify DNS propagation before proceeding with SSL certificate installation
3. WHEN DNS records are updated, THE Deployment_System SHALL wait for propagation with a timeout of 48 hours
4. THE Deployment_System SHALL configure DNS TTL values of 3600 seconds (1 hour) for production stability
5. WHERE Cloudflare is used, THE Deployment_System SHALL configure proxy settings for CDN and DDoS protection

### Requirement 3: System Dependencies Installation

**User Story:** As a system administrator, I want to install all required system packages and dependencies, so that the Django application and its components can run properly.

#### Acceptance Criteria

1. THE Deployment_System SHALL install Python 3.11 or later with pip and venv modules
2. THE Deployment_System SHALL install PostgreSQL 14 or later with development headers
3. THE Deployment_System SHALL install Redis 6.0 or later for caching and message brokering
4. THE Deployment_System SHALL install Nginx or Apache as the Web_Server
5. THE Deployment_System SHALL install Supervisor or configure systemd for Process_Manager functionality
6. THE Deployment_System SHALL install system libraries required by Playwright (libgbm, libnss3, libxss1, libasound2)
7. THE Deployment_System SHALL install build-essential, python3-dev, libpq-dev, and git packages
8. THE Deployment_System SHALL verify all installed packages meet minimum version requirements

### Requirement 4: Database Setup and Configuration

**User Story:** As a system administrator, I want to set up and configure the PostgreSQL database, so that the Django application can store and retrieve data securely.

#### Acceptance Criteria

1. THE Deployment_System SHALL create a PostgreSQL database named "examforms"
2. THE Deployment_System SHALL create a PostgreSQL user with a secure randomly-generated password
3. THE Deployment_System SHALL grant all privileges on the examforms database to the created user
4. THE Deployment_System SHALL configure PostgreSQL to accept connections from localhost only
5. THE Deployment_System SHALL set PostgreSQL shared_buffers to 25% of available RAM
6. THE Deployment_System SHALL enable PostgreSQL query logging for queries exceeding 1000ms
7. THE Deployment_System SHALL configure PostgreSQL to use UTF-8 encoding
8. THE Deployment_System SHALL create database connection pooling configuration with maximum 20 connections

### Requirement 5: Redis Configuration

**User Story:** As a system administrator, I want to configure Redis for caching and as a Celery message broker, so that the application can cache data and process background tasks efficiently.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure Redis to bind to localhost only (127.0.0.1)
2. THE Deployment_System SHALL set Redis maxmemory to 512MB with allkeys-lru eviction policy
3. THE Deployment_System SHALL enable Redis persistence with appendonly mode
4. THE Deployment_System SHALL configure Redis to save snapshots every 300 seconds if at least 10 keys changed
5. WHERE Redis password authentication is enabled, THE Deployment_System SHALL generate a secure random password
6. THE Deployment_System SHALL configure Redis to start automatically on system boot

### Requirement 6: Application Code Deployment

**User Story:** As a developer, I want to deploy the Django application code to the server, so that the application can be run in the production environment.

#### Acceptance Criteria

1. THE Deployment_System SHALL create an application directory at /var/www/examforms with appropriate permissions
2. THE Deployment_System SHALL clone or copy the application code to the application directory
3. THE Deployment_System SHALL create a Python virtual environment in the application directory
4. THE Deployment_System SHALL install all Python dependencies from requirements.txt within the virtual environment
5. THE Deployment_System SHALL install Playwright browsers using "playwright install" command
6. THE Deployment_System SHALL set ownership of application files to the Deployment_User
7. THE Deployment_System SHALL set file permissions to 755 for directories and 644 for files
8. WHERE Git is used for deployment, THE Deployment_System SHALL configure Git to ignore file permission changes

### Requirement 7: Environment Variables and Secrets Management

**User Story:** As a developer, I want to configure environment variables and secrets securely, so that sensitive configuration is not exposed in the codebase.

#### Acceptance Criteria

1. THE Deployment_System SHALL create a .env file in the application root directory with restricted permissions (600)
2. THE Deployment_System SHALL generate a secure random Django SECRET_KEY of at least 50 characters
3. THE Deployment_System SHALL set DEBUG to False for production environment
4. THE Deployment_System SHALL configure ALLOWED_HOSTS to include examforms.org and www.examforms.org
5. THE Deployment_System SHALL configure database connection parameters (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
6. THE Deployment_System SHALL configure Redis connection parameters (REDIS_HOST, REDIS_PORT)
7. THE Deployment_System SHALL configure BASE_URL to https://examforms.org
8. WHERE external services are used, THE Deployment_System SHALL configure API keys for Sentry, AdSense, and AWS services
9. THE Deployment_System SHALL ensure the .env file is owned by Deployment_User and not readable by other users

### Requirement 8: Database Migration and Initial Data

**User Story:** As a developer, I want to run database migrations and load initial data, so that the database schema is created and the application has necessary seed data.

#### Acceptance Criteria

1. WHEN database is empty, THE Deployment_System SHALL run "python manage.py migrate" to create all database tables
2. THE Deployment_System SHALL verify all migrations completed successfully before proceeding
3. IF migration fails, THEN THE Deployment_System SHALL log the error and halt deployment
4. WHERE initial data fixtures exist, THE Deployment_System SHALL load them using "python manage.py loaddata"
5. THE Deployment_System SHALL create a Django superuser account for administrative access
6. THE Deployment_System SHALL verify database connectivity before running migrations

### Requirement 9: Static and Media Files Configuration

**User Story:** As a developer, I want to configure static and media files serving, so that CSS, JavaScript, images, and user uploads are served efficiently.

#### Acceptance Criteria

1. THE Deployment_System SHALL run "python manage.py collectstatic --noinput" to gather all static files
2. THE Deployment_System SHALL create a staticfiles directory at /var/www/examforms/staticfiles
3. THE Deployment_System SHALL create a media directory at /var/www/examforms/media
4. THE Deployment_System SHALL configure Web_Server to serve static files from /static/ URL path
5. THE Deployment_System SHALL configure Web_Server to serve media files from /media/ URL path
6. THE Deployment_System SHALL set cache headers for static files with 1 year expiration
7. THE Deployment_System SHALL enable gzip compression for static files in Web_Server configuration
8. THE Deployment_System SHALL set appropriate permissions on media directory for write access by Application_Server

### Requirement 10: Web Server Configuration

**User Story:** As a system administrator, I want to configure the web server to handle HTTP requests and proxy to the Django application, so that the application is accessible via the domain.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure Web_Server to listen on port 80 for HTTP requests
2. THE Deployment_System SHALL configure Web_Server to listen on port 443 for HTTPS requests
3. THE Deployment_System SHALL configure Web_Server to redirect all HTTP requests to HTTPS
4. THE Deployment_System SHALL configure Web_Server to proxy application requests to Application_Server on port 8000
5. THE Deployment_System SHALL configure Web_Server to set proxy headers (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
6. THE Deployment_System SHALL configure Web_Server to serve static files directly without proxying
7. THE Deployment_System SHALL configure Web_Server to serve media files directly without proxying
8. THE Deployment_System SHALL enable gzip compression for text-based content types
9. THE Deployment_System SHALL set security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
10. THE Deployment_System SHALL configure Web_Server to use HTTP/2 protocol
11. THE Deployment_System SHALL set client_max_body_size to 10MB for file uploads
12. THE Deployment_System SHALL configure Web_Server to start automatically on system boot

### Requirement 11: Application Server Configuration

**User Story:** As a developer, I want to configure the WSGI application server to run the Django application, so that the application can handle web requests efficiently.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure Application_Server (Gunicorn or uWSGI) to bind to 127.0.0.1:8000
2. THE Deployment_System SHALL configure Application_Server with 4 worker processes (2 × CPU cores)
3. THE Deployment_System SHALL configure Application_Server worker class as "sync" for Django
4. THE Deployment_System SHALL configure Application_Server timeout to 30 seconds
5. THE Deployment_System SHALL configure Application_Server to use the virtual environment Python interpreter
6. THE Deployment_System SHALL configure Application_Server to load the WSGI application from admin_panel.wsgi:application
7. THE Deployment_System SHALL configure Application_Server access log to /var/log/examforms/access.log
8. THE Deployment_System SHALL configure Application_Server error log to /var/log/examforms/error.log
9. THE Deployment_System SHALL configure Application_Server to reload workers gracefully on code changes

### Requirement 12: Celery Worker Configuration

**User Story:** As a developer, I want to configure Celery workers to process background tasks, so that web scraping and other async tasks run independently of web requests.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure Task_Worker to use Redis as the message broker
2. THE Deployment_System SHALL configure Task_Worker with 2 concurrent worker processes
3. THE Deployment_System SHALL configure Task_Worker to use the virtual environment Python interpreter
4. THE Deployment_System SHALL configure Task_Worker log file at /var/log/examforms/celery_worker.log
5. THE Deployment_System SHALL configure Task_Worker to acknowledge tasks only after successful completion
6. THE Deployment_System SHALL configure Task_Worker with task time limit of 3600 seconds (1 hour)
7. THE Deployment_System SHALL configure Task_Worker to use prefork pool for task execution
8. THE Deployment_System SHALL configure Task_Worker to restart automatically on failure

### Requirement 13: Celery Beat Scheduler Configuration

**User Story:** As a developer, I want to configure Celery Beat to schedule periodic scraping tasks, so that exam information is updated automatically at specified intervals.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure Task_Scheduler to use Redis as the message broker
2. THE Deployment_System SHALL configure Task_Scheduler to store schedule in /var/www/examforms/celerybeat-schedule.db
3. THE Deployment_System SHALL configure Task_Scheduler log file at /var/log/examforms/celery_beat.log
4. THE Deployment_System SHALL configure Task_Scheduler to use the virtual environment Python interpreter
5. THE Deployment_System SHALL ensure only one Task_Scheduler instance runs at a time
6. THE Deployment_System SHALL configure Task_Scheduler to restart automatically on failure

### Requirement 14: Process Management Configuration

**User Story:** As a system administrator, I want to configure process management for all application components, so that processes start automatically and restart on failure.

#### Acceptance Criteria

1. THE Deployment_System SHALL create Process_Manager configuration for Application_Server
2. THE Deployment_System SHALL create Process_Manager configuration for Task_Worker
3. THE Deployment_System SHALL create Process_Manager configuration for Task_Scheduler
4. THE Deployment_System SHALL configure all processes to start automatically on system boot
5. THE Deployment_System SHALL configure all processes to restart automatically on failure
6. THE Deployment_System SHALL configure all processes to run as Deployment_User
7. THE Deployment_System SHALL configure all processes to redirect stderr to stdout
8. THE Deployment_System SHALL configure all processes to log to dedicated log files
9. THE Deployment_System SHALL set process priority to ensure Application_Server has higher priority than Task_Worker
10. WHERE Supervisor is used, THE Deployment_System SHALL create /etc/supervisor/conf.d/examforms.conf

### Requirement 15: SSL Certificate Installation

**User Story:** As a system administrator, I want to install and configure SSL certificates, so that the application is served over HTTPS with encrypted connections.

#### Acceptance Criteria

1. THE Deployment_System SHALL install Certbot for Let's Encrypt certificate management
2. THE Deployment_System SHALL obtain SSL_Certificate for examforms.org and www.examforms.org
3. THE Deployment_System SHALL configure Web_Server to use the obtained SSL_Certificate
4. THE Deployment_System SHALL configure Web_Server to use TLS 1.2 and TLS 1.3 protocols only
5. THE Deployment_System SHALL configure Web_Server with strong cipher suites (Mozilla Modern configuration)
6. THE Deployment_System SHALL configure automatic certificate renewal via Certbot cron job
7. THE Deployment_System SHALL verify certificate renewal process with dry-run test
8. WHERE Hostinger provides SSL certificates, THE Deployment_System SHALL use Hostinger SSL instead of Let's Encrypt
9. THE Deployment_System SHALL configure HSTS header with max-age of 31536000 seconds

### Requirement 16: Logging Configuration

**User Story:** As a developer, I want to configure comprehensive logging, so that application errors and activities can be monitored and debugged.

#### Acceptance Criteria

1. THE Deployment_System SHALL create log directory at /var/log/examforms with appropriate permissions
2. THE Deployment_System SHALL configure Django logging to write to /var/log/examforms/django.log
3. THE Deployment_System SHALL configure log rotation for all log files to rotate daily
4. THE Deployment_System SHALL configure log retention to keep logs for 14 days
5. THE Deployment_System SHALL configure log compression for rotated logs
6. THE Deployment_System SHALL set log file permissions to 640 (owner read/write, group read)
7. THE Deployment_System SHALL configure separate log files for Application_Server, Task_Worker, and Task_Scheduler
8. THE Deployment_System SHALL configure Web_Server access logs and error logs
9. WHERE Sentry is configured, THE Deployment_System SHALL enable Sentry error tracking in Django settings

### Requirement 17: Backup Strategy Implementation

**User Story:** As a system administrator, I want to implement automated backups, so that data can be recovered in case of failure or data loss.

#### Acceptance Criteria

1. THE Deployment_System SHALL create backup directory at /var/backups/examforms
2. THE Deployment_System SHALL create automated backup script for PostgreSQL database
3. THE Deployment_System SHALL configure database backups to run daily at 2:00 AM via cron
4. THE Deployment_System SHALL compress database backups using gzip
5. THE Deployment_System SHALL include timestamp in backup filenames (YYYYMMDD_HHMMSS format)
6. THE Deployment_System SHALL retain local backups for 7 days and delete older backups
7. THE Deployment_System SHALL create backup script for media files
8. THE Deployment_System SHALL configure media file backups to run weekly
9. WHERE AWS S3 is configured, THE Deployment_System SHALL upload backups to S3 bucket
10. THE Deployment_System SHALL verify backup integrity after creation
11. THE Deployment_System SHALL send notification on backup failure

### Requirement 18: Security Hardening

**User Story:** As a system administrator, I want to implement security hardening measures, so that the server and application are protected against common attacks.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure UFW firewall to allow only necessary ports (22, 80, 443)
2. THE Deployment_System SHALL install and configure fail2ban to prevent brute-force SSH attacks
3. THE Deployment_System SHALL disable password authentication for SSH (key-based only)
4. THE Deployment_System SHALL configure fail2ban jail for Nginx with 5 retry limit
5. THE Deployment_System SHALL set Django SECURE_SSL_REDIRECT to True
6. THE Deployment_System SHALL set Django SECURE_HSTS_SECONDS to 31536000
7. THE Deployment_System SHALL set Django SESSION_COOKIE_SECURE to True
8. THE Deployment_System SHALL set Django CSRF_COOKIE_SECURE to True
9. THE Deployment_System SHALL set Django SECURE_BROWSER_XSS_FILTER to True
10. THE Deployment_System SHALL set Django SECURE_CONTENT_TYPE_NOSNIFF to True
11. THE Deployment_System SHALL configure PostgreSQL to reject connections from external IPs
12. THE Deployment_System SHALL configure Redis to reject connections from external IPs
13. THE Deployment_System SHALL set restrictive file permissions on .env file (600)
14. THE Deployment_System SHALL disable directory listing in Web_Server configuration

### Requirement 19: Performance Optimization

**User Story:** As a developer, I want to implement performance optimizations, so that the application loads quickly and handles traffic efficiently.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure Django caching with Redis backend
2. THE Deployment_System SHALL set cache timeout to 3600 seconds for static content
3. THE Deployment_System SHALL enable Django template caching
4. THE Deployment_System SHALL configure Web_Server with gzip compression for text content
5. THE Deployment_System SHALL configure Web_Server with Brotli compression where supported
6. THE Deployment_System SHALL set browser cache headers for static files (1 year expiration)
7. THE Deployment_System SHALL enable HTTP/2 in Web_Server configuration
8. THE Deployment_System SHALL configure PostgreSQL connection pooling
9. THE Deployment_System SHALL configure Web_Server worker connections to 1024
10. WHERE Cloudflare is used, THE Deployment_System SHALL enable Cloudflare caching for static assets
11. THE Deployment_System SHALL configure Django to use persistent database connections

### Requirement 20: Monitoring and Health Checks

**User Story:** As a system administrator, I want to implement monitoring and health checks, so that I can detect and respond to issues proactively.

#### Acceptance Criteria

1. THE Deployment_System SHALL create a Django health check endpoint at /health/
2. THE Deployment_System SHALL configure health check endpoint to verify database connectivity
3. THE Deployment_System SHALL configure health check endpoint to verify Redis connectivity
4. THE Deployment_System SHALL configure health check endpoint to return HTTP 200 when healthy
5. IF any service is unavailable, THEN THE health check endpoint SHALL return HTTP 503
6. THE Deployment_System SHALL configure Web_Server to exclude health check requests from access logs
7. WHERE Sentry is configured, THE Deployment_System SHALL enable performance monitoring
8. THE Deployment_System SHALL create monitoring script to check disk space usage
9. THE Deployment_System SHALL create monitoring script to check memory usage
10. THE Deployment_System SHALL configure alerts when disk usage exceeds 80%
11. THE Deployment_System SHALL configure alerts when memory usage exceeds 85%

### Requirement 21: Deployment Automation

**User Story:** As a developer, I want to create deployment automation scripts, so that future deployments can be executed consistently and reliably.

#### Acceptance Criteria

1. THE Deployment_System SHALL create a deployment script that pulls latest code from repository
2. THE Deployment_System SHALL create a deployment script that installs new dependencies
3. THE Deployment_System SHALL create a deployment script that runs database migrations
4. THE Deployment_System SHALL create a deployment script that collects static files
5. THE Deployment_System SHALL create a deployment script that restarts application processes
6. THE Deployment_System SHALL create a deployment script that clears application cache
7. THE Deployment_System SHALL create a deployment script that verifies deployment success
8. IF deployment verification fails, THEN THE deployment script SHALL rollback to previous version
9. THE Deployment_System SHALL create a rollback script that reverts to previous code version
10. THE Deployment_System SHALL create a rollback script that restores previous database state
11. THE Deployment_System SHALL log all deployment actions with timestamps

### Requirement 22: Initial Deployment Verification

**User Story:** As a system administrator, I want to verify the initial deployment, so that I can confirm all components are working correctly before going live.

#### Acceptance Criteria

1. WHEN deployment is complete, THE Deployment_System SHALL verify the website loads at https://examforms.org
2. THE Deployment_System SHALL verify the Django admin panel is accessible at /admin/
3. THE Deployment_System SHALL verify static files are served correctly
4. THE Deployment_System SHALL verify database connectivity through the application
5. THE Deployment_System SHALL verify Redis connectivity through the application
6. THE Deployment_System SHALL verify Celery workers are running and processing tasks
7. THE Deployment_System SHALL verify Celery Beat scheduler is running
8. THE Deployment_System SHALL verify SSL certificate is valid and HTTPS is working
9. THE Deployment_System SHALL verify HTTP to HTTPS redirect is working
10. THE Deployment_System SHALL verify health check endpoint returns HTTP 200
11. THE Deployment_System SHALL run a test scraping task to verify Scrapy functionality
12. THE Deployment_System SHALL verify all log files are being written correctly
13. IF any verification fails, THEN THE Deployment_System SHALL report the specific failure and halt

### Requirement 23: Documentation and Handoff

**User Story:** As a system administrator, I want comprehensive deployment documentation, so that the deployment can be maintained and troubleshooted by other team members.

#### Acceptance Criteria

1. THE Deployment_System SHALL create documentation of all server credentials and access methods
2. THE Deployment_System SHALL create documentation of all environment variables and their purposes
3. THE Deployment_System SHALL create documentation of all installed services and their configurations
4. THE Deployment_System SHALL create documentation of backup and restore procedures
5. THE Deployment_System SHALL create documentation of deployment and rollback procedures
6. THE Deployment_System SHALL create documentation of monitoring and alerting setup
7. THE Deployment_System SHALL create documentation of common troubleshooting procedures
8. THE Deployment_System SHALL create documentation of log file locations and rotation policies
9. THE Deployment_System SHALL create documentation of SSL certificate renewal process
10. THE Deployment_System SHALL create runbook for handling common operational tasks
