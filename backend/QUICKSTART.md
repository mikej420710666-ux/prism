# PRISM Quick Start Guide

Get PRISM running locally in 5 minutes.

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- X Developer Account (with OAuth 2.0 app)

## Backend Setup

```bash
# 1. Navigate to backend
cd prism-backend

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your credentials (see below)

# 4. Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE prism;
CREATE USER prism_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE prism TO prism_user;
\q

# 5. Run migrations
alembic upgrade head

# 6. Start backend services (3 terminals)
# Terminal 1: API
uvicorn app.main:app --reload --port 8003

# Terminal 2: Celery Worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Celery Beat
celery -A app.celery_app beat --loglevel=info
```

## Frontend Setup

```bash
# 1. Navigate to frontend
cd prism-backend/frontend

# 2. Install dependencies
npm install

# 3. Setup environment
cp .env.example .env.local
# Edit NEXT_PUBLIC_API_URL if needed (default: http://localhost:8003)

# 4. Start dev server
npm run dev
```

## Environment Variables

### Backend `.env` (Minimum Required)

```bash
# Database
DATABASE_URL=postgresql://prism_user:your_password@localhost:5432/prism

# Redis
REDIS_URL=redis://localhost:6379/3

# Security
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# X API
X_CLIENT_ID=your_x_client_id
X_CLIENT_SECRET=your_x_client_secret
X_BEARER_TOKEN=your_x_bearer_token
X_OAUTH_CALLBACK_URL=http://localhost:8003/api/auth/callback

# AI APIs
ANTHROPIC_API_KEY=sk-ant-xxx
MISTRAL_API_KEY=xxx
GROK_API_KEY=xxx

# App
PORT=8003
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend `.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8003
```

## X Developer Portal Setup

1. Go to [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard)
2. Create a new App (OAuth 2.0)
3. Set **App Permissions**: Read and Write
4. Add **Callback URL**: `http://localhost:8003/api/auth/callback`
5. Copy **Client ID**, **Client Secret**, and **Bearer Token**
6. Update backend `.env`

## Test the Application

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8003/health
   # Should return: {"status": "healthy"}
   ```

2. **Frontend**:
   - Open [http://localhost:3000](http://localhost:3000)
   - Click "Connect X Account"
   - Authorize on X
   - You should be redirected to dashboard

3. **Voice Analysis**:
   - After OAuth, voice analysis starts automatically
   - Wait 30-60 seconds
   - Refresh dashboard to see results

4. **Discover Posts**:
   - Navigate to "Discover" in navbar
   - Enter a niche (or leave empty for auto-detect)
   - Click "Discover Posts"
   - Click "Remix with AI" on any post

5. **Schedule**:
   - In remix modal, select AI model
   - Click "Remix"
   - Choose schedule time or "Post Now"
   - View in "Schedule" page

## Common Issues

### Database Connection Failed
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U prism_user -d prism -h localhost
```

### Redis Connection Failed
```bash
# Check Redis is running
sudo systemctl status redis

# Test connection
redis-cli ping
```

### OAuth Redirect Not Working
- Verify callback URL in X Developer Portal: `http://localhost:8003/api/auth/callback`
- Check backend is running on port 8003
- Check CORS allows `http://localhost:3000`

### Celery Tasks Not Running
```bash
# Check Redis is accessible
redis-cli ping

# Check worker is running
celery -A app.celery_app inspect active
```

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed configuration
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Read [frontend/README.md](frontend/README.md) for frontend details

---

**Need help?** Check logs:
- Backend: Console output from `uvicorn` command
- Celery: Console output from `celery worker` command
- Frontend: Browser console and terminal output

Happy automating! 🚀
