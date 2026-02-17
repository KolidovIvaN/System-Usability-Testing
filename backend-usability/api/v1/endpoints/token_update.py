from fastapi import APIRouter, HTTPException, Depends
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependence import get_db
from schemas.token_update import UserToken
from services.user_auth import get_user_by_id
from utils.config import settings
from utils.security import create_access_token

router = APIRouter()


@router.post("/refresh_access_token")
async def refresh_token(token: UserToken, db: AsyncSession = Depends(get_db)):

    try:
        payload = jwt.decode(
            token.refresh_token,
            key=settings.SECURITY_KEY,
            algorithms=settings.SECURITY_ALGORITHM,
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # создаём новый access
    new_access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }