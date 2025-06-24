# app/models/users.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship

class Users(Base):
    """Model to represent the user"""
    
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Remove the companies relationship until you create the Companies model
    companies = relationship("Companies", back_populates='owner')