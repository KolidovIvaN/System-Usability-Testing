from typing import Dict, Iterator, Tuple

from pydantic import BaseModel


class DataImages(BaseModel):
    face: str

    def items(self) -> Iterator[Tuple[str, str]]:
        return self.model_dump().items()

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()


class ModelRequest(BaseModel):
    data_user_face: DataImages
    

class PredictionResult(BaseModel):
    emotions: Dict[str, float]