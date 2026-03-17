import logging
import sys
import os

from app.utils.config import settings


def setup_logging():
    
    # Создаём директорию для логов
    log_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "logs")
    )
    os.makedirs(log_path, exist_ok=True)
    
    formatter = logging.Formatter("%(asctime)s | PID:%(process)d | %(levelname)s | %(name)s | %(message)s")
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    root_logger.handlers.clear()
    
    # Console handler (dev)
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setFormatter(formatter)
    # console_handler.setLevel(getattr(logging, settings.log_level))
    # root_logger.addHandler(console_handler)
    
    if settings.log_file:
        file_handler = logging.FileHandler(
            os.path.join(log_path, settings.log_file), 
            encoding="utf-8", 
            mode="a"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, settings.log_level))
        root_logger.addHandler(file_handler)
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    logger = logging.getLogger("eyetracking")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Получить логгер с префиксом приложения"""
    return logging.getLogger(f"eyetracking.{name}")