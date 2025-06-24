from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Companies(Base):
    """model to represent the companies under a user"""
    
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, unique=True)
    company_owner = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    company_name = Column(String, nullable=False)
    company_address = Column(Text, nullable=False)
    company_gstin = Column(String, nullable=False, unique=True, default=None)
    company_msme = Column(String, nullable=True, default=None)
    company_email = Column(String, nullable=False)
    company_bank_account_no = Column(String, nullable=False)
    company_bank_name = Column(String, nullable=False)
    company_account_holder = Column(String, nullable=False)
    company_branch = Column(String, nullable=False)
    company_ifsc_code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with Users, Customers
    owner = relationship("Users", back_populates='companies')
    customers = relationship("Customers", back_populates='customer_of', lazy='selectin')
    products = relationship('Products', back_populates='product_by')
    invoice = relationship('Invoices', back_populates='invoice_by')