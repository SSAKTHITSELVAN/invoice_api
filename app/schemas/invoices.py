# app/schemas/invoices.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Assuming common.py for APIResponse and schemas for Companies/Customers exist
from app.schemas.common import APIResponse
from app.schemas.companies import CompanyOut # Assuming this exists for relationship output
from app.schemas.customers import CustomerOut # Assuming this exists for relationship output
from app.schemas.invoice_items import InvoiceItemOut # New schema for invoice items output

# Schema for creating invoice items within an invoice
class InvoiceItemInput(BaseModel):
    product_id: str # Changed to str for UUID
    invoice_item_quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

    class Config:
        from_attributes = True # Pydantic v2 compatibility

# Schema for creating a new invoice with items
class CreateInvoiceWithItems(BaseModel):
    owner_company: str # Changed to str for UUID
    customer_company: str # Changed to str for UUID
    invoice_number: str
    invoice_date: datetime
    invoice_due_date: datetime
    invoice_terms: str
    invoice_place_of_supply: str
    invoice_notes: str
    invoice_items: List[InvoiceItemInput] = Field(..., description="An invoice must have at least one item.") # Enforce items

    class Config:
        from_attributes = True

# Schema for updating an invoice (allowing partial updates)
class UpdateInvoice(BaseModel):
    # owner_company and customer_company typically not changed after creation
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    invoice_due_date: Optional[datetime] = None
    invoice_terms: Optional[str] = None
    invoice_place_of_supply: Optional[str] = None
    invoice_notes: Optional[str] = None
    # No direct update fields for totals or items here; handle via separate endpoints or full replacement
    # invoice_items: Optional[List[InvoiceItemInput]] = None # Could add this for full item replacement/update

    class Config:
        from_attributes = True

# Output schema for a single invoice item (including calculated fields)
class InvoiceItemOut(BaseModel):
    invoice_item_id: str # Changed to str for UUID
    invoice_id: str # Changed to str for UUID
    product_id: str # Changed to str for UUID
    invoice_item_quantity: int
    invoice_item_cgst_rate: float
    invoice_item_sgst_rate: float
    invoice_item_igst_rate: float # Added for IGST
    # Calculated fields for output only
    invoice_item_unit_price: float
    invoice_item_total_amount_before_tax: float
    invoice_item_cgst_amount: float
    invoice_item_sgst_amount: float
    invoice_item_igst_amount: float # Added for IGST amount
    invoice_item_total_amount: float
    created_at: datetime
    # product: Optional[ProductOut] = None # Assuming ProductOut schema exists in app.schemas.products

    class Config:
        from_attributes = True

# Output schema for an Invoice
class InvoiceOut(BaseModel):
    invoice_id: str # Changed to str for UUID
    owner_company: str # Changed to str for UUID
    customer_company: str # Changed to str for UUID
    invoice_number: str
    invoice_date: datetime
    invoice_due_date: datetime
    invoice_terms: str
    invoice_place_of_supply: str
    invoice_notes: str
    invoice_subtotal: float
    invoice_total_cgst: float
    invoice_total_sgst: float
    invoice_total_igst: float # Added for IGST
    invoice_total: float
    created_at: datetime
    invoice_by: Optional[CompanyOut] = None # Use CompanyOut for nested relationship
    client: Optional[CustomerOut] = None # Use CustomerOut for nested relationship
    products: List[InvoiceItemOut] = [] # Use InvoiceItemOut for nested items

    class Config:
        from_attributes = True

# API Response Models
class SingleInvoiceResponse(APIResponse[InvoiceOut]):
    """Response model for a single invoice."""
    pass

class ListInvoiceResponse(APIResponse[List[InvoiceOut]]):
    """Response model for a list of invoices."""
    pass