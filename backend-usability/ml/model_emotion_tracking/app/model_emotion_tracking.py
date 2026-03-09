import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from typing import Any, Dict


class ModelTrackingEmotion:
    def __init__(self) -> None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        emotion_list = ["angry", "happy", "neutral", "sad", "surprice"]
        
        global modelTrackingEmotion
        
        modelTrackingEmotion = models.resnet101(pretrained=False)
        num_ftrs = modelTrackingEmotion.fc.in_features
        modelTrackingEmotion.fc = nn.Linear(num_ftrs, len(emotion_list))

        model_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "resources", "weight", "model_emotion_tracking.pth"
            ))
        modelTrackingEmotion.load_state_dict(torch.load(model_path, map_location=device))
        modelTrackingEmotion.to(device)
        modelTrackingEmotion.eval()
    
    
    async def predict_emotion(self, img_face: Any) -> Dict[str, float]:
        with torch.no_grad():
            outputs = modelTrackingEmotion(img_face)
            probabilities = F.softmax(outputs, dim=1)
            emotions = probabilities.cpu().numpy()[0] * 100
            emotions = emotions.tolist()

            return {
                "angry": round(emotions[0], 4),
                "happy": round(emotions[1], 4),
                "neutral": round(emotions[2], 4),
                "sad": round(emotions[3], 4),
                "surprise": round(emotions[4], 4),
            }
        
        return {
            "angry": 0.0,
            "happy": 0.0,
            "neutral": 0.0,
            "sad": 0.0,
            "surprise": 0.0,
        }