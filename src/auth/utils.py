from passlib import pwd
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from src.config import Config
import jwt
from uuid import uuid4
import logging
from itsdangerous import URLSafeTimedSerializer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRY = 3600


def generate_hash_password(password: str) -> str:
    hash = pwd_context.hash(password)
    return hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Compare this snippet from src/auth/models.py:


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
) -> str:
    payload = {}
    expires_at = datetime.now(timezone.utc) + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )

    payload["user"] = user_data
    payload["exp"] = expires_at
    payload["jti"] = str(uuid4())

    payload["refresh"] = refresh

    access_token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET_KEY, algorithm=Config.ALGORITHM
    )
    return access_token


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token, Config.JWT_SECRET_KEY, algorithms=[Config.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError as e:
        logging.exception(f"Invalid token: {str(e)}")
        return None
    except jwt.InvalidTokenError:
        return None


serializer = URLSafeTimedSerializer(Config.JWT_SECRET_KEY, salt="email-configuration")


def create_url_safe_token(data: dict) -> str:
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str) -> dict:
    try:
        data = serializer.loads(token, max_age=3600)
        return data
    except Exception as e:
        logging.exception(f"Invalid token: {str(e)}")
        return None
