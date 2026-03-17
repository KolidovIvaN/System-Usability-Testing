import asyncio
import base64
import pickle
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Union

import torch
import torchvision.transforms as transforms
from PIL import Image

from app.utils.config import settings


class PreprocessingImages:
    def __init__(self, num_workers: int = None) -> None:
        self.transform_eye_model = transforms.Compose([
            transforms.ColorJitter(brightness=0.3, 
                                   contrast=0.3, 
                                   saturation=0.3, 
                                   hue=0.1),
            transforms.ToTensor()
        ])
        max_workers = num_workers or settings.preprocessing_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def _deserialize_tensor_sync(self, data: str):
        return pickle.loads(base64.b64decode(data.encode('utf-8')))
    
    def _create_img_sync(self, img):
        return Image.fromarray(img)
    
    def _transform_img_sync(self, transform, img):
        return transform(img).unsqueeze(0)
    
    def _float_tensor_sync(self, data):
        return torch.FloatTensor(data).unsqueeze(0)
    
    def preprocessing_images_sync(self, data_user_face: Union[Dict[str, str], Any]) -> Dict[str, Any]:
        def _formation_data(data: Dict[str, str]) -> Dict[str, Any]:
            return {
                "face": self._deserialize_tensor_sync(data["face"]),
                "face_pos": self._deserialize_tensor_sync(data["face_pos"]),
                "l_eye": self._deserialize_tensor_sync(data["l_eye"]),
                "r_eye": self._deserialize_tensor_sync(data["r_eye"]),
                "l_eye_geom": self._deserialize_tensor_sync(data["l_eye_geom"]),
                "r_eye_geom": self._deserialize_tensor_sync(data["r_eye_geom"]),
                "head_geom": self._deserialize_tensor_sync(data["head_geom"]),
            }

        if hasattr(data_user_face, 'model_dump'):
            data_dict = data_user_face.model_dump()
            
        elif hasattr(data_user_face, 'dict'):
            data_dict = data_user_face.dict()

        else:
            data_dict = data_user_face
        
        data_formatted = _formation_data(data_dict)
        images_eye_model = {}

        for name, img in data_formatted.items():
            if name in ["face", "face_pos", "l_eye", "r_eye"]:
                img = self._create_img_sync(img)
                
                if name == "face_pos":
                    img = transforms.ToTensor()(img).unsqueeze(0)

                else:
                    img = self._transform_img_sync(self.transform_eye_model, img)
                
                images_eye_model[name] = img

            else:
                images_eye_model[name] = self._float_tensor_sync(img)

        return images_eye_model
    
    async def preprocessing_images(
        self, data_user_face: Union[Dict[str, str], Any]
    ) -> Dict[str, Any]:

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self.preprocessing_images_sync(data_user_face)
        )