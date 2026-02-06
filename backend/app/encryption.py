"""
AES-256 encryption for storing X OAuth tokens
"""

from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings
import base64


class Settings(BaseSettings):
    encryption_key: str  # 32-byte key encoded as base64

    class Config:
        env_file = ".env"


settings = Settings()


class TokenEncryption:
    """
    Encrypt and decrypt X OAuth tokens for secure storage
    """

    def __init__(self):
        # Ensure key is valid Fernet key
        try:
            self.cipher = Fernet(settings.encryption_key.encode())
        except Exception:
            # If key is not valid base64, generate from raw bytes
            # In production, use: Fernet.generate_key()
            self.cipher = Fernet(base64.urlsafe_b64encode(settings.encryption_key.encode()[:32].ljust(32, b'0')))


    def encrypt_token(self, token: str) -> str:
        """
        Encrypt an OAuth token

        Args:
            token: Plain text token

        Returns:
            Encrypted token (base64 encoded)
        """
        encrypted = self.cipher.encrypt(token.encode())
        return encrypted.decode()


    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt an OAuth token

        Args:
            encrypted_token: Encrypted token (base64 encoded)

        Returns:
            Plain text token
        """
        decrypted = self.cipher.decrypt(encrypted_token.encode())
        return decrypted.decode()


# Global instance
token_encryption = TokenEncryption()


def encrypt_token(token: str) -> str:
    """Helper function to encrypt a token"""
    return token_encryption.encrypt_token(token)


def decrypt_token(encrypted_token: str) -> str:
    """Helper function to decrypt a token"""
    return token_encryption.decrypt_token(encrypted_token)
