from fastapi import FastAPI

from api.v1.router import api_router


app = FastAPI(
    title="UsabilityTesting",
    version="1.0.0",
)

app.include_router(router=api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app", 
        host="localhost", 
        port=5000,
    )