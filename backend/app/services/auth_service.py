import datetime
import hashlib
import os
from typing import Optional, Dict, Any
from app.config import settings

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password securely using bcrypt or salt-hashed sha256."""
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            salt = os.urandom(16).hex()
            h = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
            return f"sha256${salt}${h}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against the stored hash."""
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            if BCRYPT_AVAILABLE:
                return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            return False
        elif hashed_password.startswith("sha256$"):
            parts = hashed_password.split("$")
            if len(parts) == 3:
                salt, stored_hash = parts[1], parts[2]
                computed = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
                return computed == stored_hash
        return False

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
        """Creates a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        if JWT_AVAILABLE:
            encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            return encoded_jwt
        else:
            # Fallback simple token if jwt is loading
            return f"dristhi_{to_encode.get('sub', 'anonymous')}_{int(expire.timestamp())}"

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """Decodes and validates a JWT token."""
        if not JWT_AVAILABLE:
            return None
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except Exception:
            return None

auth_service = AuthService()
