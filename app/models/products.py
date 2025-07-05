# app/models/products.py
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Products(Base):
    __tablename__ = 'products'
    company_id = Column(String(36), ForeignKey('companies.company_id', ondelete='CASCADE'))
    product_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_name = Column(String, nullable=False)
    product_description = Column(Text, nullable=False)
    product_hsn_sac_code = Column(String, nullable=False)
    product_unit_of_measure = Column(String, nullable=False, default='set')
    product_unit_price = Column(Float, nullable=False)
    product_default_cgst_rate = Column(Float, nullable=False)
    product_default_sgst_rate = Column(Float, nullable=False)
    product_default_igst_rate = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product_by = relationship('Companies', back_populates='products')
    # Relationship to InvoiceItems for products included in invoices
    invoice_items = relationship('InvoiceItems', back_populates='product', lazy='selectin')