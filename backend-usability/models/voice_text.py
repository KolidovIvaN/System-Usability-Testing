from sqlalchemy import Column, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class VoiceText(Base):
    __tablename__ = "voice"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    start_voice = Column(Float, nullable=True)
    end_voice = Column(Float, nullable=True)

    participant_id = Column(Integer, ForeignKey("participants.id"))
    participant = relationship("Participant", back_populates="voice")

