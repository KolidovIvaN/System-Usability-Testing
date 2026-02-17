from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import AsyncSessionLocal
from models.users import Users
from services.user_auth import get_user_by_id
from utils.config import settings


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Users:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token,
            key=settings.SECURITY_KEY,
            algorithms=settings.SECURITY_ALGORITHM,
        )

        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired",
        )
    
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(db=db, id=int(user_id))

    if user is None:
        raise credentials_exception

    return user
