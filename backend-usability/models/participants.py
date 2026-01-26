from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    pc_skill_level = Column(Integer)

    usability_test_id = Column(Integer, ForeignKey("usability_tests.id"))
    usability_tests = relationship("UsabilityTests", back_populates="participants")

    gaze_point = relationship("GazePoint", back_populates="participants")
    emotions = relationship("Emotions", back_populates="participants")
    voice = relationship("VoiceText", back_populates="participants")
    mouse_point = relationship("MousePoint", back_populates="participants")
    feedback = relationship("Feedback", uselist=False, back_populates="participants")
