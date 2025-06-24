# ============================================================================
# SCHEMAS - invoices.py (Updated)
# ============================================================================

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.schemas.companies import CreateCompany
from app.schemas.customers import CreateCustomer
from app.schemas.invoice_items import InvoiceItems

class CreateInvoice(BaseModel):
    owner_company: int
    customer_company: int
    invoice_number: str
    invoice_date: datetime
    invoice_due_date: datetime
    invoice_terms: str
    invoice_place_of_supply: str
    invoice_notes: str
    invoice_subtotal: float
    invoice_total_cgst: float
    invoice_total_sgst: float
    invoice_total: float
    
    class Config:
        orm_mode = True

class UpdateInvoice(BaseModel):
    owner_company: Optional[int] = None
    customer_company: Optional[int] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    invoice_due_date: Optional[datetime] = None
    invoice_terms: Optional[str] = None
    invoice_place_of_supply: Optional[str] = None
    invoice_notes: Optional[str] = None
    invoice_subtotal: Optional[float] = None
    invoice_total_cgst: Optional[float] = None
    invoice_total_sgst: Optional[float] = None
    invoice_total: Optional[float] = None
    
    class Config:
        orm_mode = True

class InvoiceOut(BaseModel):
    invoice_id: int
    owner_company: int
    customer_company: int
    invoice_number: str
    invoice_date: datetime
    invoice_due_date: datetime
    invoice_terms: str
    invoice_place_of_supply: str
    invoice_notes: str
    invoice_subtotal: float
    invoice_total_cgst: float
    invoice_total_sgst: float
    invoice_total: float
    created_at: datetime
    invoice_by: Optional[CreateCompany] = None
    client: Optional[CreateCustomer] = None
    products: List[InvoiceItems] = []
    
    class Config:
        orm_mode = True


class InvoiceItemInput(BaseModel):
    product_id: int
    quantity: int
    
    class Config:
        orm_mode = True


class CreateInvoiceWithItems(BaseModel):
    invoice_data: CreateInvoice
    invoice_items: List[InvoiceItemInput]
    
    class Config:
        orm_mode = True
