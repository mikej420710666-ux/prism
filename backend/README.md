# PRISM Backend

X growth automation tool - AI-powered tweet remixing and scheduling.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database (prism)
- **Redis** - Caching & Celery broker (DB 3)
- **SQLAlchemy + Alembic** - ORM & migrations
- **Celery** - Background job processing
- **OAuth 2.0** - X account authentication
- **AI APIs** - Claude, Mistral, Grok

## Features

1. **X Account Connection** - OAuth 2.0 integration
2. **Voice Analysis** - Analyze user's tweets to detect niche and writing style
3. **Viral Post Discovery** - Search X for high-performing content in user's niche
4. **AI Remixing** - Transform viral posts into user's unique voice
5. **Scheduling** - Queue remixed posts for automated publishing
6. **Auto-pilot Mode** - Fully automated content generation and posting

## Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Initialize Database**
```bash
alembic upgrade head
```

4. **Run Development Server**
```bash
uvicorn app.main:app --reload --port 8003
```

5. **Start Celery Worker**
```bash
celery -A app.celery_app worker --loglevel=info
```

## Project Structure

```
prism-backend/
├── app/
│   ├── main.py              # FastAPI app + routes
│   ├── database.py          # SQLAlchemy connection
│   ├── models.py            # DB models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # JWT + OAuth
│   ├── x_api.py             # X API integration
│   ├── ai_service.py        # AI APIs (Claude/Mistral/Grok)
│   ├── celery_app.py        # Celery config + tasks
│   ├── encryption.py        # Token encryption (AES-256)
│   └── dependencies.py      # FastAPI dependencies
├── requirements.txt
├── .env.example
└── README.md
```

## Running on VPS

Service runs on port **8003** alongside:
- MindSync
- Halo Gate
- Roundtable

Will be configured as systemd service for production deployment.
