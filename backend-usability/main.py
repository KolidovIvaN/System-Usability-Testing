import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.v1.auth import router as auth_router

from database.base import Base
from database.engine import engine
from models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы (ТОЛЬКО ДЛЯ РАЗРАБОТКИ!)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield

    await engine.dispose()


app = FastAPI(
    title="UsabilityTesting",
    version="1.0.0"
)

app.include_router(auth_router)

@app.get(path="/health")
async def health_server():
    return {"server_status": "200"}


if __name__ == "__main__":
    uvicorn.run(
        app="main:app", 
        host="localhost", 
        port=5000, 
        reload=True,
        workers=2
    )