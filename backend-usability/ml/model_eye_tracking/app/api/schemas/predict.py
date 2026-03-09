from typing import Dict, Iterator, Tuple

from pydantic import BaseModel


class DataImages(BaseModel):
    face: str
    face_pos: str
    l_eye: str
    r_eye: str
    l_eye_geom: str
    r_eye_geom: str
    head_geom: str

    def items(self) -> Iterator[Tuple[str, str]]:
        return self.model_dump().items()

    def keys(self):
        return self.model_dump().keys()

    def values(self):
        return self.model_dump().values()


class ModelRequest(BaseModel):
    data_user_face: DataImages
    

class PredictionResult(BaseModel):
    eye_coordinates: Dict[str, int]