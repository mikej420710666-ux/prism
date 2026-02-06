# PRISM Backend Setup Guide

Complete setup instructions for PRISM - X Growth Automation Backend.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- X (Twitter) Developer Account with OAuth 2.0 credentials

## Quick Start

### 1. Install Dependencies

```bash
cd prism-backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Database
DATABASE_URL=postgresql://prism_user:your_password@localhost:5432/prism

# Redis
REDIS_URL=redis://localhost:6379/3

# X API OAuth 2.0
X_CLIENT_ID=your_x_client_id
X_CLIENT_SECRET=your_x_client_secret
X_BEARER_TOKEN=your_x_bearer_token
X_OAUTH_CALLBACK_URL=https://prism.six7vault.com/api/auth/callback

# AI APIs
ANTHROPIC_API_KEY=sk-ant-your-key
MISTRAL_API_KEY=your-mistral-key
GROK_API_KEY=your-grok-key
GROK_BASE_URL=https://api.x.ai/v1

# Security
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# App
PORT=8003
ALLOWED_ORIGINS=http://localhost:3000,https://prism.six7vault.com
```

### 3. Create Database

```bash
# PostgreSQL
sudo -u postgres psql
CREATE DATABASE prism;
CREATE USER prism_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE prism TO prism_user;
\q
```

### 4. Run Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 5. Start Services

**Development:**

```bash
# Terminal 1: API Server
uvicorn app.main:app --reload --port 8003

# Terminal 2: Celery Worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Celery Beat (for scheduled tasks)
celery -A app.celery_app beat --loglevel=info
```

**Production (systemd):**

See `DEPLOYMENT.md` for systemd service setup.

## API Endpoints

### Authentication

- `GET /api/auth/connect` - Start X OAuth flow
- `GET /api/auth/callback` - OAuth callback
- `GET /api/auth/me` - Get current user

### Voice Analysis

- `POST /api/user/voice/analyze` - Trigger voice analysis
- `GET /api/user/voice` - Get voice profile

### Health

- `GET /` - API info
- `GET /health` - Health check

## OAuth Flow

1. User clicks "Connect X Account" → Frontend calls `/api/auth/connect`
2. Frontend redirects user to `authorization_url` from response
3. User authorizes on X
4. X redirects to `/api/auth/callback?code=...&state=...`
5. Backend exchanges code for tokens, stores encrypted tokens
6. Returns JWT token to frontend
7. Background task analyzes user's voice automatically

## Rate Limits

PRISM enforces X API rate limits:
- **Post tweets**: 100 per 15 minutes
- Tracked in Redis with automatic retry

## Security Features

- OAuth 2.0 with PKCE
- AES-256 encryption for X tokens
- JWT authentication for API
- CSRF protection with state parameter
- Never logs sensitive tokens

## Background Jobs

### Celery Tasks

1. **analyze_user_voice** - Analyze tweets to build voice profile
2. **post_scheduled_tweet** - Post tweets with rate limiting
3. **discover_viral_posts** - Search X for viral content
4. **auto_pilot** - Full automation workflow
5. **process_scheduled_posts** - Cron: posts due tweets
6. **run_auto_pilot_users** - Cron: runs auto-pilot for enabled users

## Testing

```bash
# Run API
uvicorn app.main:app --reload --port 8003

# Test OAuth flow
curl http://localhost:8003/api/auth/connect

# Test health
curl http://localhost:8003/health
```

## Troubleshooting

### Database connection fails
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify DATABASE_URL in `.env`

### Redis connection fails
- Check Redis is running: `sudo systemctl status redis`
- Verify REDIS_URL uses DB 3: `redis://localhost:6379/3`

### X API errors
- Check X Developer Portal for API credentials
- Verify OAuth callback URL matches `.env` and X app settings
- Check rate limits in X Developer Portal

### Celery not processing tasks
- Ensure Redis is running (Celery broker)
- Check worker logs: `celery -A app.celery_app worker --loglevel=debug`

## Next Steps

1. Deploy to VPS on port 8003
2. Set up systemd services
3. Configure nginx reverse proxy
4. Build frontend (Next.js)
5. Test end-to-end OAuth flow

---

Built with ❤️ for X growth automation
