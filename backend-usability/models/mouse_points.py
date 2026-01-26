from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class MousePoint(Base):
    __tablename__ = "mouse_points"

    id = Column(Integer, primary_key=True, index=True)
    x = Column(Float)
    y = Column(Float)
    timestamp = Column(Float, nullable=True)

    participant_id = Column(Integer, ForeignKey("participants.id"))
    participant = relationship("Participant", back_populates="mouse_points")
