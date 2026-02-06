"""
Authentication & OAuth helpers
JWT token creation and X OAuth 2.0 flow
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import httpx
import secrets
import hashlib
import base64
from urllib.parse import urlencode
from app.database import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


# X OAuth 2.0 URLs
X_OAUTH_AUTHORIZE_URL = "https://twitter.com/i/oauth2/authorize"
X_OAUTH_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
X_OAUTH_REVOKE_URL = "https://api.twitter.com/2/oauth2/revoke"

# Required OAuth scopes
X_OAUTH_SCOPES = [
    "tweet.read",
    "tweet.write",
    "users.read",
    "follows.read",
    "follows.write"
]


def generate_pkce_pair() -> tuple[str, str]:
    """
    Generate PKCE code_verifier and code_challenge

    Returns:
        (code_verifier, code_challenge)
    """
    # Generate code_verifier (43-128 chars)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    code_verifier = code_verifier.rstrip('=')  # Remove padding

    # Generate code_challenge using SHA256
    challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8')
    code_challenge = code_challenge.rstrip('=')  # Remove padding

    return code_verifier, code_challenge


def get_x_oauth_url(state: str) -> tuple[str, str]:
    """
    Generate X OAuth 2.0 authorization URL with PKCE

    Args:
        state: Random state string for CSRF protection

    Returns:
        (authorization_url, code_verifier) - Store code_verifier in session/redis for callback
    """
    code_verifier, code_challenge = generate_pkce_pair()

    # Use x_oauth_callback_url if set, otherwise use x_redirect_uri
    redirect_uri = settings.x_oauth_callback_url or settings.x_redirect_uri
    
    params = {
        "response_type": "code",
        "client_id": settings.x_client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(X_OAUTH_SCOPES),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    authorization_url = f"{X_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"

    return authorization_url, code_verifier


async def exchange_code_for_token(code: str, code_verifier: str) -> Dict:
    """
    Exchange OAuth authorization code for access token

    Args:
        code: Authorization code from callback
        code_verifier: PKCE code_verifier from initial request

    Returns:
        {
            "access_token": "...",
            "refresh_token": "...",
            "expires_in": 7200,
            "token_type": "bearer"
        }

    Raises:
        httpx.HTTPError: If token exchange fails
    """
    # Use x_oauth_callback_url if set, otherwise use x_redirect_uri
    redirect_uri = settings.x_oauth_callback_url or settings.x_redirect_uri
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            X_OAUTH_TOKEN_URL,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": settings.x_client_id,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier
            },
            auth=(settings.x_client_id, settings.x_client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()


async def refresh_x_token(refresh_token: str) -> Dict:
    """
    Refresh expired X access token

    Args:
        refresh_token: User's refresh token

    Returns:
        {
            "access_token": "...",
            "refresh_token": "...",
            "expires_in": 7200,
            "token_type": "bearer"
        }

    Raises:
        httpx.HTTPError: If refresh fails
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            X_OAUTH_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.x_client_id
            },
            auth=(settings.x_client_id, settings.x_client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()


async def revoke_x_token(token: str, token_type: str = "access_token") -> bool:
    """
    Revoke an X access or refresh token

    Args:
        token: Token to revoke
        token_type: "access_token" or "refresh_token"

    Returns:
        True if successful
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            X_OAUTH_REVOKE_URL,
            data={
                "token": token,
                "token_type_hint": token_type,
                "client_id": settings.x_client_id
            },
            auth=(settings.x_client_id, settings.x_client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.status_code == 200
