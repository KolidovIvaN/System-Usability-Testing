from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.token_update import router as authenticator_router

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)

api_router.include_router(
    authenticator_router,
    prefix="/token_update",
    tags=["token_update"]
)