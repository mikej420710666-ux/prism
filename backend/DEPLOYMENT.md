# PRISM Deployment Guide

Complete deployment guide for both backend and frontend.

## Architecture Overview

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Frontend   │──────▶│   Backend    │──────▶│  PostgreSQL  │
│   Next.js    │       │   FastAPI    │       │   Database   │
│   Port 3000  │       │   Port 8003  │       │              │
└──────────────┘       └──────────────┘       └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │    Redis     │
                       │   + Celery   │
                       └──────────────┘
```

## Prerequisites

- **VPS/Server** with Ubuntu 22.04+ or similar
- **Domain name** with DNS configured
- **SSL Certificate** (Let's Encrypt recommended)
- **X Developer Account** with OAuth 2.0 app configured
- **API Keys** for Claude, Mistral, and Grok

## Backend Deployment (VPS)

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install nginx
sudo apt install nginx -y
```

### 2. Setup PostgreSQL Database

```bash
sudo -u postgres psql

CREATE DATABASE prism;
CREATE USER prism_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE prism TO prism_user;
\q
```

### 3. Setup Project

```bash
# Clone repo (or copy files via rsync/scp)
cd /home/username
git clone https://github.com/yourusername/prism-backend.git
cd prism-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
nano .env
```

Update values:

```bash
DATABASE_URL=postgresql://prism_user:your_secure_password@localhost:5432/prism
REDIS_URL=redis://localhost:6379/3

SECRET_KEY=<generate with: openssl rand -hex 32>
ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

X_CLIENT_ID=your_x_client_id
X_CLIENT_SECRET=your_x_client_secret
X_BEARER_TOKEN=your_x_bearer_token
X_OAUTH_CALLBACK_URL=https://api.prism.yourdomain.com/api/auth/callback

ANTHROPIC_API_KEY=sk-ant-xxx
MISTRAL_API_KEY=xxx
GROK_API_KEY=xxx

PORT=8003
FRONTEND_URL=https://prism.yourdomain.com
ALLOWED_ORIGINS=https://prism.yourdomain.com,https://prism-*.vercel.app
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Setup Systemd Services

**API Service** (`/etc/systemd/system/prism-api.service`):

```ini
[Unit]
Description=PRISM FastAPI Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=username
WorkingDirectory=/home/username/prism-backend
Environment="PATH=/home/username/prism-backend/venv/bin"
ExecStart=/home/username/prism-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003
Restart=always

[Install]
WantedBy=multi-user.target
```

**Celery Worker** (`/etc/systemd/system/prism-celery.service`):

```ini
[Unit]
Description=PRISM Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=username
WorkingDirectory=/home/username/prism-backend
Environment="PATH=/home/username/prism-backend/venv/bin"
ExecStart=/home/username/prism-backend/venv/bin/celery -A app.celery_app worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

**Celery Beat** (`/etc/systemd/system/prism-celery-beat.service`):

```ini
[Unit]
Description=PRISM Celery Beat Scheduler
After=network.target redis.service

[Service]
Type=simple
User=username
WorkingDirectory=/home/username/prism-backend
Environment="PATH=/home/username/prism-backend/venv/bin"
ExecStart=/home/username/prism-backend/venv/bin/celery -A app.celery_app beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable prism-api prism-celery prism-celery-beat
sudo systemctl start prism-api prism-celery prism-celery-beat

# Check status
sudo systemctl status prism-api
sudo systemctl status prism-celery
```

### 7. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/prism-api`:

```nginx
server {
    listen 80;
    server_name api.prism.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/prism-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.prism.yourdomain.com
```

### 9. Verify Backend

```bash
curl https://api.prism.yourdomain.com/health
# Should return: {"status": "healthy"}
```

---

## Frontend Deployment (Vercel)

### 1. Push to GitHub

```bash
cd frontend
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/prism-frontend.git
git push -u origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Connect GitHub repo
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend/`
   - **Environment Variables**:
     - `NEXT_PUBLIC_API_URL=https://api.prism.yourdomain.com`

5. Click "Deploy"

### 3. Custom Domain (Optional)

In Vercel dashboard:
1. Go to Project Settings → Domains
2. Add `prism.yourdomain.com`
3. Configure DNS:
   - Type: CNAME
   - Name: prism
   - Value: cname.vercel-dns.com

### 4. Update Backend CORS

In backend `.env`, add Vercel domains:

```bash
ALLOWED_ORIGINS=https://prism.yourdomain.com,https://prism-*.vercel.app
```

Restart backend:

```bash
sudo systemctl restart prism-api
```

---

## Alternative: Frontend on VPS (with Backend)

If deploying frontend on same VPS:

### 1. Build Frontend

```bash
cd /home/username/prism-backend/frontend
npm install
npm run build
```

### 2. Setup PM2 (Process Manager)

```bash
sudo npm install -g pm2
pm2 start npm --name "prism-frontend" -- start
pm2 save
pm2 startup
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/prism-frontend`:

```nginx
server {
    listen 80;
    server_name prism.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and setup SSL:

```bash
sudo ln -s /etc/nginx/sites-available/prism-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d prism.yourdomain.com
```

---

## X Developer Portal Configuration

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create OAuth 2.0 App
3. **App Permissions**: Read and Write
4. **Callback URLs**:
   - Development: `http://localhost:8003/api/auth/callback`
   - Production: `https://api.prism.yourdomain.com/api/auth/callback`
5. **Website URL**: `https://prism.yourdomain.com`
6. Copy **Client ID**, **Client Secret**, and **Bearer Token**
7. Update backend `.env`

---

## Monitoring & Logs

### Backend Logs

```bash
# API logs
sudo journalctl -u prism-api -f

# Celery worker logs
sudo journalctl -u prism-celery -f

# Celery beat logs
sudo journalctl -u prism-celery-beat -f
```

### Frontend Logs (Vercel)

View in Vercel dashboard → Project → Deployments → View Function Logs

### Database Monitoring

```bash
sudo -u postgres psql prism
SELECT * FROM users LIMIT 10;
SELECT COUNT(*) FROM scheduled_posts WHERE status = 'pending';
```

### Redis Monitoring

```bash
redis-cli
INFO
KEYS *
GET rate_limit:user_1:x_posts
```

---

## Backup Strategy

### Database Backup

Create daily backup script (`/home/username/backup-prism.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/home/username/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump prism > $BACKUP_DIR/prism_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "prism_*.sql" -mtime +7 -delete
```

Add to crontab:

```bash
crontab -e
# Add: 0 2 * * * /home/username/backup-prism.sh
```

---

## Scaling Considerations

### Horizontal Scaling

- Use **Gunicorn** with multiple workers for FastAPI
- Run multiple Celery workers on different machines
- Use **PostgreSQL replication** for read replicas
- Use **Redis Cluster** for distributed rate limiting

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database with indexes
- Use Redis connection pooling

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u prism-api -n 50

# Test manually
cd /home/username/prism-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8003
```

### Celery not processing tasks

```bash
# Check Redis connection
redis-cli ping

# Check worker logs
sudo journalctl -u prism-celery -n 50

# List active tasks
celery -A app.celery_app inspect active
```

### OAuth redirect fails

- Verify callback URL in X Developer Portal matches backend `.env`
- Check CORS configuration allows frontend origin
- Ensure SSL certificate is valid

### Database connection errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U prism_user -d prism -h localhost
```

---

## Security Checklist

- [ ] Strong passwords for database and encryption keys
- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured (UFW or iptables)
- [ ] SSH key-only authentication (disable password login)
- [ ] Environment variables not committed to git
- [ ] Regular security updates (`apt update && apt upgrade`)
- [ ] Rate limiting enabled on API endpoints
- [ ] CORS properly configured (no `*` in production)
- [ ] X OAuth tokens encrypted in database

---

## Support

For issues, check:
- Backend logs: `sudo journalctl -u prism-api -f`
- Frontend logs: Vercel dashboard
- Database status: `sudo systemctl status postgresql`
- Redis status: `sudo systemctl status redis`

---

Built with ❤️ for X growth automation
