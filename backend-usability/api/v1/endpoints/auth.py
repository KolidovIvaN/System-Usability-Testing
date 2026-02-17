from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependence import get_db, get_current_user
from models.users import Users
from schemas.user import UserRegister, UserLogin
from services.user_auth import create_user, authenticate_user, get_user_by_id
from utils.security import create_access_token, create_refresh_token

router = APIRouter()

@router.post("/register")
async def register_user(
    user_data: UserRegister, 
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await create_user(db=db, user_data=user_data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=f"User {user_data.email} was successfully created"
        )

    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
async def login_user(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    
    try:
        user: Users = await authenticate_user(db=db, user_data=user_data)
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                }
            }
        )
        
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error server: {e}"
        )

@router.get("/me")
async def me(current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_user_by_id(db=db, id=current_user.id)
