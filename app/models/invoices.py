from app.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from datetime import datetime
from sqlalchemy.orm import relationship

class Invoices(Base):
    __tablename__ = 'invoices'
    
    invoice_id = Column(Integer, primary_key=True, index=True)
    owner_company = Column(Integer, ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False)
    customer_company = Column(Integer, ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    invoice_number = Column(String(100), nullable=False)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    invoice_due_date = Column(DateTime, default=datetime.utcnow)
    invoice_terms = Column(Text, nullable=False)
    invoice_place_of_supply = Column(String(100), nullable=False)
    invoice_notes = Column(Text, nullable=False)
    invoice_subtotal = Column(Float, nullable=False)
    invoice_total_cgst = Column(Float, nullable=False)
    invoice_total_sgst = Column(Float, nullable=False)
    invoice_total_gst = Column(Float, nullable=False)
    invoice_total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice_by = relationship('Companies', back_populates='invoice', lazy='selectin')
    client = relationship('Customers', back_populates='invoice_for', lazy='selectin')
    products = relationship('InvoiceItems', back_populates='invoice', lazy='selectin')
    
