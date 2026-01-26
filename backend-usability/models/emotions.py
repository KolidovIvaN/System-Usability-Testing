from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class Emotions(Base):
    __tablename__ = "emotions"

    id = Column(Integer, primary_key=True, index=True)
    neutral = Column(Float)
    sadness = Column(Float)
    disgust = Column(Float)
    happiness = Column(Float)
    surprise = Column(Float)
    timestamp = Column(Float, nullable=True)

    participant_id = Column(Integer, ForeignKey("participants.id"))
    participant = relationship("Participant", back_populates="emotions")
