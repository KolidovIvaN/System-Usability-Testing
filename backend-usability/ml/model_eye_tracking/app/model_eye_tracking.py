import os
import torch
from typing import Any, Dict

from app.resources.model_config import MODEL_CONFIG
from app.resources.model_architecture import ArchitectureEyeTrackingModel


class ModelEyeTracking:
    def __init__(self) -> None:
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        global modelEyeTracking
        
        model_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "resources", "weight", "model_eye_tracking.pth"))
        
        modelEyeTracking = ArchitectureEyeTrackingModel(config=MODEL_CONFIG)
        modelEyeTracking.load_state_dict(torch.load(model_path))
        modelEyeTracking.eval()
        
    async def predictor_eye_coordinates(self, data: Dict[str, Any]) -> Dict[str, int]:
        try:
            with torch.no_grad():
                outputs = modelEyeTracking(
                    data["face"],
                    data["face_pos"],
                    data["l_eye"],
                    data["r_eye"],
                    data["l_eye_geom"],
                    data["r_eye_geom"],
                    data["head_geom"],
                )
                
                coordinates = outputs.squeeze().tolist()

            return {"X": int(coordinates[0]),
                    "Y": int(coordinates[1])}
        
        except Exception as e:
            raise(f"Error while eye tracking model predict: {e}") from e