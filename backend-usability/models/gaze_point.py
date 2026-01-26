from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from database.base import Base


class GazePoint(Base):
    __tablename__ = "gaze_points"

    id = Column(Integer, primary_key=True, index=True)
    x = Column(Float)
    y = Column(Float)
    timestamp = Column(Float, nullable=True)

    participant_id = Column(Integer, ForeignKey("participants.id"))
    participant = relationship("Participant", back_populates="gaze_points")
