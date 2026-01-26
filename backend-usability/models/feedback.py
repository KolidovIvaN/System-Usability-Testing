from sqlalchemy import Column, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)

    participant_id = Column(Integer, ForeignKey("participants.id"), unique=True)
    participant = relationship("Participant", back_populates="feedback")