from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String(50))
    last_name = Column(String(50))

    tests = relationship("UsabilityTests", back_populates="owner")
