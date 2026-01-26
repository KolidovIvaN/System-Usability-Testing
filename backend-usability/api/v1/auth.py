from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import get_db
from schemas.user import UserRegister
from services.user_auth import create_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register")
async def register_user(
    user_data: UserRegister, 
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await create_user(db=db, user_data=user_data)
        return {"status": status.HTTP_201_CREATED,
                "detail": f"User {user_data.email} was successfully created"}
    
    except Exception as e:
        print(f"ERROR: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


