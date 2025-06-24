from pydantic import BaseModel
from typing import Optional
from enum import Enum as PyEnum


class CreateProduct(BaseModel):
    company_id: int
    product_name: str
    product_description: str
    product_hsn_sac_code: str
    product_unit_of_measure: str
    product_unit_price: float
    product_default_cgst_rate: float
    product_default_sgst_rate: float
    product_default_igst_rate: float
    
    class Config:
        orm_mode = True

class UpdateProduct(CreateProduct):
    pass