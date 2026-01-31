from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from models.users import Users
from schemas.user import UserRegister
from utils.security import get_password_hash


async def get_user_by_email(db:AsyncSession, email: str) -> Optional[str]:
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()

async def create_user(db:AsyncSession, user_data: UserRegister) -> Users:
    existing_user = await get_user_by_email(
        db=db,
        email=user_data.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    hashed_pass = get_password_hash(password=user_data.password)

    new_user = Users(
        email=user_data.email,
        password=hashed_pass,
        first_name=user_data.first_name,  
        last_name=user_data.last_name
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
