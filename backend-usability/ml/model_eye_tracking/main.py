import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.model_predict import router as predict_router
from app.model_eye_tracking import ModelEyeTracking
from app.preprocessing import PreprocessingImages
from app.worker_pool import ModelWorkerPool, PreprocessingWorkerPool
from app.utils.config import settings
from app.utils.logger import setup_logging


logger = setup_logging()


def model_factory(device: str):
    return ModelEyeTracking(device=device)

def preprocessing_factory():
    return PreprocessingImages()

@asynccontextmanager
async def lifespan(app_: FastAPI):
    logger.info(f"Starting application EyeTracker")
    
    try:
        # Инициализация пулов
        app_.state.model_pool = ModelWorkerPool(
            model_factory=model_factory,
            device=settings.model_device,
            workers_count=settings.model_workers,
            worker_type=settings.model_worker_type
        )
        await app_.state.model_pool.initialize()
        
        app_.state.preprocessing_pool = PreprocessingWorkerPool(
            preprocessing_factory=preprocessing_factory,
            workers_count=settings.preprocessing_workers
        )
        await app_.state.preprocessing_pool.initialize()
        
        logger.info("All worker pools initialized successfully")
        
    except Exception as e:
        logger.critical(f"Initialization error: {e}", exc_info=True)
        sys.exit(1)
    
    yield
    
    try:
        logger.info("Shutting down application...")
        if hasattr(app_.state, 'model_pool'):
            await app_.state.model_pool.shutdown()
            
        if hasattr(app_.state, 'preprocessing_pool'):
            await app_.state.preprocessing_pool.shutdown()
        
        logger.info("Shutdown complete")

    except Exception as e:
        logger.critical(f"Error while shudwon: {e}")

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