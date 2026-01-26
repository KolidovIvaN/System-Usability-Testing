import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.v1.auth import router as auth_router

from database.base import Base
from database.engine import engine
from models import *
from utils.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Подключение к БД: {settings.get_url_database}")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        raise
    
    yield
    
    await engine.dispose()


app = FastAPI(
    title="UsabilityTesting",
    version="1.0.0",
    lifespan=lifespan
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
    )