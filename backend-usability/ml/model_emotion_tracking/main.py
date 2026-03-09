import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.utils.config import settings
from app.utils.logger import setup_logging
from app.model_emotion_tracking import ModelWorkerPool
from app.preprocessing import PreprocessingImages
from app.api.v1.model_predict import router as predict_router


# Настройка логирования
logger = setup_logging(
    log_level=settings.log_level, 
    log_file=settings.log_file
)

@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Конфигурация
    settings.print_config()
    logger.info(f"Application startup | Device: {settings.resolved_device}")
    
    try:
        # Инициализация компонентов с параметрами
        app_.state.preprocessing = PreprocessingImages(
            num_workers=settings.preprocessing_workers
        )
        
        app_.state.model_pool = ModelWorkerPool(
            device=settings.resolved_device,
            pool_size=settings.model_pool_size
        )
        
        app_.state.config = settings
        
        logger.info("All components initialized successfully")
        
        yield
        
    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        sys.exit(1)
    
    try:
        logger.info("Application shutdown started...")
        app_.state.preprocessing.shutdown()
        app_.state.model_pool.shutdown()
        logger.info(f"Application shutdown complete")

    except Exception as e:
        logger.warning(f"Error while application shutdown: {e}")
    

app = FastAPI(
    title="EmotionTracking",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    router=predict_router,
    prefix="/emotion-tracking",
    tags=["emotion-tracking"]
)
