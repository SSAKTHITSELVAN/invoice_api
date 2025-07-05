# app/models/invoices.py
from app.database import Base
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, func
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid

class Invoices(Base):
    __tablename__ = 'invoices'

    invoice_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    # Foreign key for the company that owns the invoice
    owner_company = Column(String(36), ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False)
    # Foreign key for the customer (from the Customers model) that receives the invoice
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

    # Relationships:
    # Relationship to the owning company
    owner_company_rel = relationship(
        'Companies',
        back_populates='invoices_owned', # Must match the name in Companies model
        foreign_keys=[owner_company],     # Explicitly use the owner_company column
        lazy='selectin'
    )

    # Relationship to the customer (from the Customers model)
    client = relationship(
        'Customers',
        back_populates='invoice_for',    # Must match the relationship name in Customers model
        foreign_keys=[customer_company], # Explicitly use the customer_company column
        lazy='selectin'
    )

    # Relationship to InvoiceItems
    invoice_items = relationship(
        'InvoiceItems',
        back_populates='invoice',        # Must match the name in InvoiceItems model
        lazy='selectin',
        cascade="all, delete-orphan"
    )