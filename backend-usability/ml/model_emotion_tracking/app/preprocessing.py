import base64
import pickle
from typing import Any, Dict

import torchvision.transforms as transforms
from PIL import Image


class PreprocessingImages:
    def __init__(self) -> None:
        self.transform_emotion_model = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
    
    async def deserialize_tensor(self, data: str):
        """Преобразует base64 строку обратно в тензор"""
        return pickle.loads(base64.b64decode(data.encode('utf-8')))
    
    async def preprocessing_images(
        self, data_user_face: Dict[str, str]
    ) -> Dict[str, str]:
        
        async def _create_img(img):
            return Image.fromarray(img)
        
        async def _transform_img(transform, img):
            return transform(img).unsqueeze(0)
        
        async def _foramtion_data(data_user_face: Dict[str, str]) -> Dict[str, Any]:
            return {
                "face": await self.deserialize_tensor(data=data_user_face.face),
            }
        
        data_user_face = await _foramtion_data(data_user_face=data_user_face)
        
        images_emotion_model = {}

        images_emotion_model["face"] = await _transform_img(
            transform=self.transform_emotion_model,
            img=await _create_img(img=data_user_face["face"])
        )
        
        return images_emotion_model