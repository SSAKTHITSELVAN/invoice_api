# app/models/users.py
from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship
import uuid

class Users(Base):
    """Model to represent the user"""

    __tablename__ = "users"
    user_id = Column(String(36), primary_key=True, default= lambda : str(uuid.uuid4()))
    user_name = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship with Companies
    companies = relationship("Companies", back_populates='owner')