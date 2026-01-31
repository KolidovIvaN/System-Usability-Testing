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
    usability_tests = relationship("UsabilityTests", back_populates="participant")

    gaze_points = relationship("GazePoint", back_populates="participant")
    emotions = relationship("Emotions", back_populates="participant")
    voice = relationship("VoiceText", back_populates="participant") 
    mouse_points = relationship("MousePoint", back_populates="participant")
    feedback = relationship("Feedback", uselist=False, back_populates="participant")
