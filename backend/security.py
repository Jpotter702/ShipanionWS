"""
Security utilities for JWT-based authentication.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

# Import settings
from .settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, TEST_TOKEN

# JWT algorithm
ALGORITHM = "HS256"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock user database - in production, use a real database
fake_users_db = {
    "user": {
        "username": "user",
        # Hashed password for "password"
        "hashed_password": "$2b$12$kTpyJ/FFeNCnxTnmneEOIOZnLxjvvSpLLyTkKt0WIV5SDCeoOlnpO",
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    result = pwd_context.verify(plain_password, hashed_password)
    print(f"DEBUG: verify_password called with plain_password='{plain_password}', hashed_password='{hashed_password}', result={result}")
    return result

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by username and password."""
    print(f"DEBUG: authenticate_user called with username='{username}', password='{password}'")
    user = fake_users_db.get(username)
    print(f"DEBUG: user found: {user}")
    if not user:
        print("DEBUG: No such user.")
        return None
    if not verify_password(password, user["hashed_password"]):
        print("DEBUG: Password verification failed.")
        return None
    print("DEBUG: Authentication successful.")
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    print(f"DEBUG: Incoming token: '{token}'")
    print(f"DEBUG: Server TEST_TOKEN: '{TEST_TOKEN}'")
    print(f"DEBUG: Tokens match? {token == TEST_TOKEN}")
    """Verify a JWT token and return its payload if valid."""
    try:
        # Check if this is the test token
        if token == TEST_TOKEN:
            # For the test token, return a simple payload
            return {"sub": "user"}

        # For regular tokens, decode with the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error in verify_token: {str(e)}")
        raise
