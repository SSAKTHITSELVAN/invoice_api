# app/models/invoice_items.py
from app.database import Base
from sqlalchemy import Column, String, ForeignKey, DateTime, Float, Integer, func
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid

class InvoiceItems(Base):
    __tablename__ = 'invoice_items'

    invoice_id = Column(String(36), ForeignKey('invoices.invoice_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(String(36), ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)
    invoice_item_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    invoice_item_quantity = Column(Integer, nullable=False)
    invoice_item_cgst_rate = Column(Float, default=0.0)
    invoice_item_sgst_rate = Column(Float, default=0.0)
    invoice_item_igst_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    invoice = relationship('Invoices', back_populates='invoice_items', lazy='selectin')
    product = relationship('Products', back_populates='invoice_items', lazy='selectin')