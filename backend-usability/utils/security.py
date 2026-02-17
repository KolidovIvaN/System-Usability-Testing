from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt

from utils.config import settings

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=16
)

def get_password_hash(password: str) -> str:
    if len(password.encode("utf-8")) > 1024:
        raise ValueError("Password too long")
    
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    
    except VerifyMismatchError:
        return False

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:

    # Копируем данные, чтобы не изменять оригинальный словарь
    to_encode = data.copy()
    
    # Устанавливаем время истечения токена
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.SECURITY_ACCESS_TOKEN
        )
    
    # Добавляем время истечения в данные токена
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    return jwt.encode(
            to_encode, 
            key=settings.SECURITY_KEY, 
            algorithm=settings.SECURITY_ALGORITHM,
        )

def create_refresh_token(data: Dict) -> str:
    """"""

    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(days=settings.SECURITY_REFRESH_TOKEN)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    return jwt.encode(
        to_encode, 
        key=settings.SECURITY_KEY, 
        algorithm=settings.SECURITY_ALGORITHM,
    )