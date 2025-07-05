# app/schemas/customers.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Import APIResponse for consistent responses
from app.schemas.common import APIResponse

class CreateCustomer(BaseModel):
    customer_to: str # Changed to str for UUID
    customer_name: str
    customer_address_line1: str
    customer_address_line2: Optional[str] = None # Made optional if it can be empty
    customer_city: str
    customer_state: str
    customer_postal_code: str
    customer_country: str
    customer_gstin: Optional[str] = None # Made optional, as it might not always be provided
    customer_email: EmailStr
    customer_phone: str

    class Config:
        orm_mode = True
        from_attributes = True # Pydantic v2 compatibility

class UpdateCustomer(BaseModel): # Changed to allow partial updates
    customer_name: Optional[str] = None
    customer_address_line1: Optional[str] = None
    customer_address_line2: Optional[str] = None
    customer_city: Optional[str] = None
    customer_state: Optional[str] = None
    customer_postal_code: Optional[str] = None
    customer_country: Optional[str] = None
    customer_gstin: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class CustomerOut(BaseModel):
    customer_id: str # Changed to str for UUID
    customer_to: str # Changed to str for UUID
    customer_name: str
    customer_address_line1: str
    customer_address_line2: Optional[str] = None
    customer_city: str
    customer_state: str
    customer_postal_code: str
    customer_country: str
    customer_gstin: Optional[str] = None
    customer_email: EmailStr
    customer_phone: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# Response models using the common APIResponse template
class SingleCustomerResponse(APIResponse[CustomerOut]):
    """Response model for a single customer."""
    pass

class ListCustomerResponse(APIResponse[List[CustomerOut]]):
    """Response model for a list of customers."""
    pass