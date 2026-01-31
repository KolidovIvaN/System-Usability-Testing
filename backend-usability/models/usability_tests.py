from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class UsabilityTests(Base):
    __tablename__ = "usability_tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    target_url = Column(String, nullable=True)
    duration_min = Column(Integer)
    description = Column(Text, nullable=True)
    participant_count = Column(Integer, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("Users", back_populates="tests")

    participant = relationship("Participant", back_populates="usability_tests")
