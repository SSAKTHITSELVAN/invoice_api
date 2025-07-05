# app/schemas/products.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import APIResponse for consistent responses (assuming app.schemas.common exists)
from app.schemas.common import APIResponse

class CreateProduct(BaseModel):
    company_id: str # Changed to str for UUID
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
        from_attributes = True # Pydantic v2 compatibility

class UpdateProduct(BaseModel): # Changed to allow partial updates
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_hsn_sac_code: Optional[str] = None
    product_unit_of_measure: Optional[str] = None
    product_unit_price: Optional[float] = None
    product_default_cgst_rate: Optional[float] = None
    product_default_sgst_rate: Optional[float] = None
    product_default_igst_rate: Optional[float] = None

    class Config:
        orm_mode = True
        from_attributes = True

class ProductOut(BaseModel):
    product_id: str # Changed to str for UUID
    company_id: str # Changed to str for UUID
    product_name: str
    product_description: str
    product_hsn_sac_code: str
    product_unit_of_measure: str
    product_unit_price: float
    product_default_cgst_rate: float
    product_default_sgst_rate: float
    product_default_igst_rate: float
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Response models using the common APIResponse template
class SingleProductResponse(APIResponse[ProductOut]):
    """Response model for a single product."""
    pass

class ListProductResponse(APIResponse[List[ProductOut]]):
    """Response model for a list of products."""
    pass