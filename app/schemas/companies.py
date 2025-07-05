# app/schemas/companies.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Assuming you have app.schemas.customers.CreateCustomer defined.
# If not, you might need a placeholder or remove the dependency for now.
# from app.schemas.customers import CreateCustomer # This line might cause issues if CreateCustomer is not ready.
# For now, let's assume CreateCustomer is a simple BaseModel for demonstration.
class CreateCustomer(BaseModel): # Placeholder for demonstration
    customer_name: str
    # ... other customer fields

# Import APIResponse for consistent responses
from app.schemas.common import APIResponse

class CreateCompany(BaseModel):
    company_owner: str # Changed to str for UUID
    company_name: str
    company_address: str
    company_gstin: Optional[str] = None
    company_msme: Optional[str] = None
    company_email: EmailStr
    company_bank_account_no: str
    company_bank_name: str
    company_account_holder: str
    company_branch: str
    company_ifsc_code: str

    class Config:
        orm_mode = True
        from_attributes = True # Added for Pydantic v2

class UpdateCompany(BaseModel): # Changed from inheriting CreateCompany to allow partial updates
    company_owner: Optional[str] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_gstin: Optional[str] = None
    company_msme: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_bank_account_no: Optional[str] = None
    company_bank_name: Optional[str] = None
    company_account_holder: Optional[str] = None
    company_branch: Optional[str] = None
    company_ifsc_code: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class CompanyOut(BaseModel):
    company_id: str # Changed to str for UUID
    company_owner: str # Changed to str for UUID
    company_name: str
    company_address: str
    company_gstin: Optional[str] = None
    company_msme: Optional[str] = None
    company_email: EmailStr
    company_bank_account_no: str
    company_bank_name: str
    company_account_holder: str
    company_branch: str
    company_ifsc_code: str
    created_at: datetime
    # customers: List[CreateCustomer] = [] # Commented out if Customers model is not fully defined yet

    class Config:
        orm_mode = True
        from_attributes = True

# Response models using the common APIResponse template
class SingleCompanyResponse(APIResponse[CompanyOut]):
    """Response model for a single company."""
    pass

class ListCompanyResponse(APIResponse[List[CompanyOut]]):
    """Response model for a list of companies."""
    pass