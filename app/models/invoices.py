# app/models/invoices.py
from app.database import Base
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, func
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid

class Invoices(Base):
    __tablename__ = 'invoices'

    invoice_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    owner_company = Column(String(36), ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False)
    customer_company = Column(String(36), ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)

    invoice_number = Column(String(100), nullable=False)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    invoice_due_date = Column(DateTime, default=datetime.utcnow)
    invoice_terms = Column(Text, nullable=False)
    invoice_place_of_supply = Column(String(100), nullable=False)
    invoice_notes = Column(Text, nullable=False)

    invoice_subtotal = Column(Float, nullable=False, default=0.0)
    invoice_total_cgst = Column(Float, nullable=False, default=0.0)
    invoice_total_sgst = Column(Float, nullable=False, default=0.0)
    invoice_total_igst = Column(Float, nullable=False, default=0.0)
    invoice_total = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # New fields for production standard
    invoice_status = Column(String(50), nullable=False, default="pending") # e.g., "pending", "paid", "partially paid", "cancelled"
    user_reference_notes = Column(Text, nullable=True) # Internal notes for user reference, not for invoice form

    # Relationships:
    owner_company_rel = relationship(
        'Companies',
        back_populates='invoices_owned',
        foreign_keys=[owner_company],
        lazy='selectin'
    )

    client = relationship(
        'Customers',
        back_populates='invoice_for',
        foreign_keys=[customer_company],
        lazy='selectin'
    )

    invoice_items = relationship(
        'InvoiceItems',
        back_populates='invoice',
        lazy='selectin',
        cascade='all, delete-orphan' # Ensure items are deleted with invoice
    )