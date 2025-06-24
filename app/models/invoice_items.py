from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from datetime import datetime
from sqlalchemy.orm import relationship

class InvoiceItems(Base):
    __tablename__ = 'invoice_items'
    
    invoice_id = Column(Integer, ForeignKey('invoices.invoice_id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'))
    invoice_item_id = Column(Integer, primary_key=True)
    invoice_item_quantity = Column(Integer, nullable=False)
    invoice_item_cgst_rate = Column(Float, default=0)
    invoice_item_sgst_rate = Column(Float, default=0)
    invoice_item_cgst_amount = Column(Float, default=0)
    invoice_item_sgst_amount = Column(Float, default=0)
    invoice_item_total = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship('Invoices', back_populates='products', lazy='selectin')
    product = relationship('Products', lazy='selectin')