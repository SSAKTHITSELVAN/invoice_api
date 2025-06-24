from pydantic import BaseModel, EmailStr
from typing import Optional

class CreateCustomer(BaseModel):
    customer_to: int
    customer_name: str
    customer_address_line1: str
    customer_address_line2: str
    customer_city: str
    customer_state: str
    customer_postal_code: str
    customer_country: str
    customer_gstin: str
    customer_email: str
    customer_phone: str
    
    class Config:
        orm_mode = True

class UpdateCustomer(CreateCustomer):
    pass