import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.model_predict import router as predict_router
from app.model_eye_tracking import ModelEyeTracking
from app.preprocessing import PreprocessingImages


@asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        app_.state.model = ModelEyeTracking()
        app_.state.preprocessing = PreprocessingImages()
    
    except Exception as e:
        print(f"Model or Preprocessor initialization error: {e}")
        sys.exit(1)
    
    yield


app = FastAPI(
    title="EyeTracking",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    router=predict_router,
    prefix="/eye-tracking",
    tags=["eye-tracking"]
)