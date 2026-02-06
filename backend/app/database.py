from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis & Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    # X API OAuth
    x_client_id: str
    x_client_secret: str
    x_redirect_uri: str
    x_bearer_token: Optional[str] = None
    x_oauth_callback_url: Optional[str] = None
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 10080
    
    # Encryption
    encryption_key: str
    
    # AI APIs
    anthropic_api_key: str
    mistral_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None
    grok_base_url: str = "https://api.x.ai/v1"
    
    # App Settings
    app_name: str = "PRISM"
    app_env: str = "development"
    port: int = 8003
    
    # Frontend
    frontend_url: str
    allowed_origins: str
    backend_url: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

settings = Settings()

# Database setup
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
