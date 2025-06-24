from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Products(Base):
    __tablename__ = 'products'
    company_id = Column(Integer, ForeignKey('companies.company_id', ondelete='CASCADE'))
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    product_description = Column(Text, nullable=False)
    product_hsn_sac_code = Column(String, nullable=False)
    product_unit_of_measure = Column(String, nullable=False, default='set')
    product_unit_price = Column(Float, nullable=False)
    product_default_cgst_rate = Column(Float, nullable=False)
    product_default_sgst_rate = Column(Float, nullable=False)
    product_default_igst_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product_by = relationship('Companies', back_populates='products')