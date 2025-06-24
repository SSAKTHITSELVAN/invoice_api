from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.schemas.customers import CreateCustomer

class CreateCompany(BaseModel):
    company_owner: int
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

class UpdateCompany(CreateCompany):
    pass

class CompanyOut(CreateCompany):
    customers: List[CreateCustomer] = []