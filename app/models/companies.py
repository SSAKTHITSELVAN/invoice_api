# app/models/companies.py
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid

class Companies(Base):
    """model to represent the companies under a user"""

    __tablename__ = "companies"
    company_id = Column(String(36), primary_key=True, unique=True, default=lambda: str(uuid.uuid4()))
    company_owner = Column(String(36), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # Relationships
    owner = relationship("Users", back_populates='companies')
    customers = relationship("Customers", back_populates='customer_of', lazy='selectin')
    products = relationship('Products', back_populates='product_by')

    # Relationship for invoices where this company is the owner
    invoices_owned = relationship(
        'Invoices',
        back_populates='owner_company_rel',
        foreign_keys="[Invoices.owner_company]", # Explicitly state the foreign key
        cascade="all, delete-orphan"
    )
    # Removed invoices_received:
    # This relationship is not needed here because Invoices.customer_company
    # points to Customers.customer_id, not Companies.company_id.
    # Invoices received by a company are conceptually linked via its Customers.