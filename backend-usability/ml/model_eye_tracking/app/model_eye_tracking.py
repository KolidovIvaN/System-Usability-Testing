import os
import torch
from typing import Any, Dict

from app.resources.model_config import MODEL_CONFIG
from app.resources.model_architecture import ArchitectureEyeTrackingModel
from app.utils.logger import get_logger
from app.utils.config import settings


logger = get_logger("model_eye_tracking")


class ModelEyeTracking:
    def __init__(self, device: str = None) -> None:
        self.device = torch.device(
            device or settings.model_device 
            if settings.model_device != "cuda" or torch.cuda.is_available() 
            else "cpu"
        )
        
        model_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "resources", "weight", "model_eye_tracking_1.0.0.pth"
        ))
        
        logger.info(f"Loading model from {model_path} to {self.device}")
        
        self.model = ArchitectureEyeTrackingModel(config=MODEL_CONFIG)
        
        if self.device.type == "cuda":
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))

        else:
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
        
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"Model loaded successfully")
    
    def predictor_eye_coordinates(self, data: Dict[str, Any]) -> Dict[str, int]:
        try:
            with torch.no_grad():
                inputs = {k: v.to(self.device) if hasattr(v, 'to') else v for k, v in data.items()}
                
                outputs = self.model(
                    inputs["face"],
                    inputs["face_pos"],
                    inputs["l_eye"],
                    inputs["r_eye"],
                    inputs["l_eye_geom"],
                    inputs["r_eye_geom"],
                    inputs["head_geom"],
                )
                
                coordinates = outputs.squeeze().cpu().tolist()

            return {"X": int(coordinates[0]), "Y": int(coordinates[1])}
        
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            raise RuntimeError(f"Error while eye-tracking model predict: {e}") from e