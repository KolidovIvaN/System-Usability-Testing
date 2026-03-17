import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Executor
from typing import Any, Dict, Optional, Callable, TypeVar
from dataclasses import dataclass

import torch

from app.utils.logger import get_logger


T = TypeVar('T')
logger = get_logger("worker_pool")


@dataclass
class WorkerTask:
    func: Callable
    args: tuple
    kwargs: dict
    future: asyncio.Future


class ModelWorkerPool:
    """
    Пул воркеров для ML-модели.
    
    - При model_worker_type='process': каждый воркер в отдельном процессе (важно для GPU)
    - При model_worker_type='thread': воркеры в потоках (для CPU-моделей)
    """
    
    def __init__(self, model_factory: Callable, device: str, workers_count: int, worker_type: str = "process"):
        self.model_factory = model_factory
        self.device = device
        self.workers_count = workers_count
        self.worker_type = worker_type
        self._executor: Optional[Executor] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._initialized = False
        self._logger = get_logger("model_worker_pool")
        
    async def initialize(self):
        if self._initialized:
            return
            
        self._loop = asyncio.get_running_loop()
        
        if self.worker_type == "process":
            # ProcessPoolExecutor для изоляции CUDA-контекстов
            self._executor = ProcessPoolExecutor(
                max_workers=self.workers_count,
                initializer=self._init_process_worker,
                initargs=(self.model_factory, self.device)
            )
            self._logger.info(f"Initialized {self.workers_count} process workers for model")
        else:
            # ThreadPoolExecutor - модель загружается в главном процессе
            self._executor = ThreadPoolExecutor(max_workers=self.workers_count)
            self._shared_model = self.model_factory(device=self.device)
            self._logger.info(f"Initialized {self.workers_count} thread workers for model")
        
        self._initialized = True
    
    def _init_process_worker(self, model_factory: Callable, device: str):
        if device == "cuda":
            torch.cuda.set_device(0)
            
        global _worker_model
        _worker_model = model_factory(device=device)
        self._logger.info(f"Process worker initialized | Device: {device}")
    
    async def predict(self, data: Dict[str, Any]) -> Dict[str, int]:
        if not self._initialized:
            await self.initialize()
        
        loop = self._loop or asyncio.get_running_loop()
        
        if self.worker_type == "process":
            result = await loop.run_in_executor(
                self._executor,
                _process_predict_wrapper,
                data
            )
        else:
            result = await loop.run_in_executor(
                self._executor,
                lambda: self._shared_model.predictor_eye_coordinates(data)
            )
        
        return result
    
    async def shutdown(self):
        if self._executor:
            self._executor.shutdown(wait=True, cancel_futures=True)
            self._logger.info("Model worker pool shutdown complete")
        self._initialized = False


def _process_predict_wrapper(data: Dict[str, Any]) -> Dict[str, int]:
    global _worker_model
    return _worker_model.predictor_eye_coordinates(data)


class PreprocessingWorkerPool:
    """Пул для CPU-интенсивного препроцессинга изображений"""
    
    def __init__(self, preprocessing_factory: Callable, workers_count: int):
        self.preprocessing_factory = preprocessing_factory
        self.workers_count = workers_count
        self._executor: Optional[ThreadPoolExecutor] = None
        self._preprocessor: Optional[Any] = None
        self._logger = get_logger("preprocessing_worker_pool")
    
    async def initialize(self):
        self._executor = ThreadPoolExecutor(max_workers=self.workers_count)
        self._preprocessor = self.preprocessing_factory()
        self._logger.info(f"Initialized preprocessing pool with {self.workers_count} threads ")
    
    async def process(self, data_user_face: Any) -> Dict[str, Any]:
        if not self._executor:
            await self.initialize()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            lambda: self._preprocessor.preprocessing_images_sync(data_user_face)
        )
        return result
    
    async def shutdown(self):
        if self._executor:
            self._executor.shutdown(wait=True)
            self._logger.info("Preprocessing pool shutdown complete")