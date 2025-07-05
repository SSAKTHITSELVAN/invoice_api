# app/models/customers.py
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Customers(Base):
    __tablename__ = 'customers'
    customer_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_to = Column(String(36), ForeignKey("companies.company_id", ondelete="CASCADE"))
    customer_name = Column(String, nullable=False)
    customer_address_line1 = Column(Text, nullable=False)
    customer_address_line2 = Column(Text, nullable=False)
    customer_city = Column(String, nullable=False)
    customer_state = Column(String, nullable=False)
    customer_postal_code = Column(String, nullable=False)
    customer_country = Column(String, nullable=False)
    customer_gstin = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    customer_of = relationship('Companies', back_populates='customers')
    # Relationship for invoices linked to this customer
    invoice_for = relationship('Invoices', back_populates='client')