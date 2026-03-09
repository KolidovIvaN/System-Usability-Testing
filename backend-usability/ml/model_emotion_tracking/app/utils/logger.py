import logging
import os
import sys

def setup_logging(log_level: str = "INFO", log_file: str = None):
    
    log_format = "%(asctime)s | PID:%(process)d | %(levelname)s | %(name)s | %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        log_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "logs"
        ))
        os.makedirs(log_path, exist_ok=True)
        
        log_file = os.path.join(log_path, log_file)
        
        handlers.append(logging.FileHandler(log_file, encoding="utf-8", mode="a"))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        handlers=handlers,
        force=True
    )
    
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)