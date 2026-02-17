from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from models.users import Users
from schemas.user import UserRegister, UserLogin
from utils.security import get_password_hash, verify_password


async def get_user_by_email(db:AsyncSession, email: str) -> Optional[Users]:
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db:AsyncSession, id: int) -> Optional[Users]:
    result = await db.execute(select(Users).where(Users.id == id))
    return result.scalar_one_or_none()


async def create_user(db:AsyncSession, user_data: UserRegister) -> Users:
    existing_user: Users = await get_user_by_email(
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

async def authenticate_user(db: AsyncSession, user_data: UserLogin) -> Optional[Users]:
    """"""

    user: Users = await get_user_by_email(
        db=db,
        email=user_data.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user with the specified email does not exist",
        )
    
    if not verify_password(plain_password=user_data.password,
                           hashed_password=user.password):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    
    return user