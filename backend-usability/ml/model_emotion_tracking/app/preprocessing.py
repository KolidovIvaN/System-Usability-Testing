import base64
import pickle
import asyncio
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

import torch
import torchvision.transforms as transforms
from PIL import Image


logger = logging.getLogger(__name__)


class PreprocessingImages:
    def __init__(self, num_workers: int = 4) -> None:
        self.num_workers = num_workers
        self.transform_emotion_model = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        
        self._executor = ThreadPoolExecutor(
            max_workers=num_workers,
            thread_name_prefix="preprocessing_worker"
        )
        logger.info(f"PreprocessingImages initialized | Workers: {num_workers}")
    
    def _deserialize_sync(self, data: str) -> Any:
        """Синхронная десериализация"""
        return pickle.loads(base64.b64decode(data.encode('utf-8')))
    
    def _process_image_sync(self, img_array: Any) -> torch.Tensor:
        """Синхронная обработка изображения"""
        
        img = Image.fromarray(img_array)
        return self.transform_emotion_model(img).unsqueeze(0)
    
    async def preprocessing_images(
        self, data_user_face: Dict[str, str]
    ) -> Dict[str, torch.Tensor]:
        """Асинхронный препроцессинг с выносом в executor"""
        
        loop = asyncio.get_running_loop()
        
        try:
            # Десериализация в отдельном потоке
            face_array = await loop.run_in_executor(
                self._executor,
                lambda: self._deserialize_sync(data_user_face.face)
            )
            
            # Обработка изображения в отдельном потоке
            processed_face = await loop.run_in_executor(
                self._executor,
                lambda: self._process_image_sync(face_array)
            )
            
            logger.debug(
                f"Preprocessing completed | "
                f"Thread: {asyncio.current_task().get_name()}"
            )
            
            return {"face": processed_face}
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}", exc_info=True)
            raise
    
    def shutdown(self):
        """Завершение executor"""

        self._executor.shutdown(wait=True)
        logger.info("PreprocessingImages shutdown complete")