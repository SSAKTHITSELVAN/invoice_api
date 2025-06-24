from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Customers(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    customer_to = Column(Integer, ForeignKey("companies.company_id", ondelete="CASCADE"))
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
    created_at = Column(DateTime, default=datetime.utcnow())
    
    customer_of = relationship('Companies', back_populates='customers')
    invoice_for = relationship('Invoices', back_populates='client')
    