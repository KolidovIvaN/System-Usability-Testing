import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


logger = logging.getLogger(__name__)


class EmotionModel:
    """Инкапсуляция модели с привязкой к устройству"""
    
    def __init__(self, model_path: str, device: str, worker_id: int = 0):
        self.worker_id = worker_id
        self.device = torch.device(device)
        self.emotion_labels = ["angry", "happy", "neutral", "sad", "surprise"]
        
        logger.info(
            f"[Worker #{worker_id}] Loading model on {self.device}"
        )
        
        # Загрузка архитектуры
        model = models.resnet101(pretrained=False)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(self.emotion_labels))
        
        # Загрузка весов
        model.load_state_dict(
            torch.load(model_path, map_location=self.device, weights_only=True)
        )
        model.to(self.device)
        model.eval()
        
        self._model = model
        
        if self.device.type == "cuda":
            torch.cuda.empty_cache()
        
        logger.info(f"[Worker #{worker_id}] Model ready")

    def _predict_sync(self, img_face: torch.Tensor) -> Dict[str, float]:
        """Синхронный инференс — вызывается в executor"""
        
        with torch.no_grad():
            input_tensor = img_face.to(self.device, non_blocking=True)
            outputs = self._model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)
            emotions = probabilities.cpu().numpy()[0] * 100
            
            return {
                label: round(float(value), 4) 
                for label, value in zip(self.emotion_labels, emotions)
            }

class ModelWorkerPool:
    def __init__(
        self, 
        device: str,
        pool_size: int
    ):
        self.device = device
        self.pool_size = pool_size
        model_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "resources", "emotion_model", "model_emotion_tracking_1.0.0.pth"
        ))
        
        self._executor = ThreadPoolExecutor(
            max_workers=pool_size,
            thread_name_prefix=f"model_worker_{device}"
        )

        logger.info(
            f"Using ThreadPoolExecutor | Device: {device} | "
            f"Workers: {pool_size}"
        )
        
        self._workers: List[EmotionModel] = []
        for i in range(pool_size):
            worker = EmotionModel(model_path, device, worker_id=i)
            self._workers.append(worker)
        
        logger.info(
            f"ModelWorkerPool initialized | Device: {device} | "
            f"Workers: {pool_size}"
        )
    
    def _run_prediction(worker: EmotionModel, img_face: torch.Tensor) -> Dict[str, float]:
        """Модульная функция для run_in_executor (не lambda!)"""
        return worker._predict_sync(img_face)

    async def predict(self, img_face: torch.Tensor, worker_id: Optional[int] = None) -> Dict[str, float]:
        """Асинхронный вызов предсказания"""
        
        if worker_id is None:
            worker_id = hash(str(id(img_face))) % self.pool_size
        
        worker = self._workers[worker_id]
        
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            ModelWorkerPool._run_prediction,
            worker,
            img_face
        )
    
    def shutdown(self):
        """Корректное завершение работы пула"""

        logger.info("Shutting down ModelWorkerPool...")
        self._executor.shutdown(wait=True, cancel_futures=True)

        if self.device == "cuda":
            torch.cuda.empty_cache()

        logger.info("ModelWorkerPool shutdown complete")