import base64
import pickle
from typing import Any, Dict

import torch
import torchvision.transforms as transforms
from PIL import Image


class PreprocessingImages:
    def __init__(self) -> None:
        self.transform_eye_model = transforms.Compose(
            [transforms.ColorJitter(
                    brightness=0.3,
                    contrast=0.3, 
                    saturation=0.3, 
                    hue=0.1),
             transforms.ToTensor()]
        )    
    
    async def deserialize_tensor(self, data: str):
        """Преобразует base64 строку обратно в тензор"""
        return pickle.loads(base64.b64decode(data.encode('utf-8')))
    
    async def preprocessing_images(
        self, data_user_face: Dict[str, str]
    ) -> Dict[str, Dict[str, str]]:
        
        async def _create_img(img):
            return Image.fromarray(img)
        
        async def _transform_img(transform, img):
            return transform(img).unsqueeze(0)
        
        async def _float_tensor(data):
            return torch.FloatTensor(data).unsqueeze(0)
        
        async def _foramtion_data(data_user_face: Dict[str, str]) -> Dict[str, Any]:
            return {
                "face": await self.deserialize_tensor(data=data_user_face.face),
                "face_pos": await self.deserialize_tensor(data=data_user_face.face_pos),
                "l_eye": await self.deserialize_tensor(data=data_user_face.l_eye),
                "r_eye": await self.deserialize_tensor(data=data_user_face.r_eye),
                "l_eye_geom": await self.deserialize_tensor(data=data_user_face.l_eye_geom),
                "r_eye_geom": await self.deserialize_tensor(data=data_user_face.r_eye_geom),
                "head_geom": await self.deserialize_tensor(data=data_user_face.head_geom),
            }
        
        data_user_face = await _foramtion_data(data_user_face=data_user_face)
        
        images_eye_model = {}

        for name, img in data_user_face.items():
            if name in ["face", "face_pos", "l_eye", "r_eye"]:
                img = await _create_img(img=img)
                
                if name == "face_pos":
                    img = transforms.ToTensor()(img).unsqueeze(0)
                
                else:
                    img = await _transform_img(
                        transform=self.transform_eye_model, img=img
                    )
                
                images_eye_model[name] = img
            
            else:
                images_eye_model[name] = await _float_tensor(data=img)

        return images_eye_model
