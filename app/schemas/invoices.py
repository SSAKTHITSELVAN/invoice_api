# # # app/schemas/invoices.py
# # from pydantic import BaseModel, Field
# # from datetime import datetime
# # from typing import List, Optional

# # # Assuming common.py for APIResponse and schemas for Companies/Customers exist
# # from app.schemas.common import APIResponse
# # from app.schemas.companies import CompanyOut # Assuming this exists for relationship output
# # from app.schemas.customers import CustomerOut # Assuming this exists for relationship output
# # from app.schemas.products import ProductOut # ADD THIS IMPORT
# # from app.schemas.invoice_items import InvoiceItemOut # New schema for invoice items output (this will be updated)

# # # Schema for creating invoice items within an invoice
# # class InvoiceItemInput(BaseModel):
# #     product_id: str # Changed to str for UUID
# #     invoice_item_quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

# #     class Config:
# #         from_attributes = True # Pydantic v2 compatibility

# # # Schema for creating a new invoice with items
# # class CreateInvoiceWithItems(BaseModel):
# #     owner_company: str # Changed to str for UUID
# #     customer_company: str # Changed to str for UUID
# #     invoice_number: str
# #     invoice_date: datetime
# #     invoice_due_date: datetime
# #     invoice_terms: str
# #     invoice_place_of_supply: str
# #     invoice_notes: str
# #     invoice_items: List[InvoiceItemInput] = Field(..., description="An invoice must have at least one item.") # Enforce items

# #     class Config:
# #         from_attributes = True

# # # Schema for updating an invoice (allowing partial updates)
# # class UpdateInvoice(BaseModel):
# #     # owner_company and customer_company typically not changed after creation
# #     invoice_number: Optional[str] = None
# #     invoice_date: Optional[datetime] = None
# #     invoice_due_date: Optional[datetime] = None
# #     invoice_terms: Optional[str] = None
# #     invoice_place_of_supply: Optional[str] = None
# #     invoice_notes: Optional[str] = None
# #     # No direct update fields for totals or items here; handle via separate endpoints or full replacement
# #     # invoice_items: Optional[List[InvoiceItemInput]] = None # Could add this for full item replacement/update

# #     class Config:
# #         from_attributes = True

# # # Output schema for a single invoice item (including calculated fields)
# # class InvoiceItemOut(BaseModel): # This InvoiceItemOut needs to be updated.
# #     invoice_item_id: str # Changed to str for UUID
# #     invoice_id: str # Changed to str for UUID
# #     product_id: str # Changed to str for UUID
# #     invoice_item_quantity: int
# #     invoice_item_cgst_rate: float
# #     invoice_item_sgst_rate: float
# #     invoice_item_igst_rate: float # Added for IGST
# #     # Calculated fields for output only
# #     invoice_item_unit_price: float
# #     invoice_item_total_amount_before_tax: float
# #     invoice_item_cgst_amount: float
# #     invoice_item_sgst_amount: float
# #     invoice_item_igst_amount: float # Added for IGST amount
# #     invoice_item_total_amount: float
# #     created_at: datetime
# #     product: Optional[ProductOut] = None # UNCOMMENT THIS LINE

# #     class Config:
# #         from_attributes = True

# # # Output schema for an Invoice
# # class InvoiceOut(BaseModel):
# #     invoice_id: str # Changed to str for UUID
# #     owner_company: str # Changed to str for UUID
# #     customer_company: str # Changed to str for UUID
# #     invoice_number: str
# #     invoice_date: datetime
# #     invoice_due_date: datetime
# #     invoice_terms: str
# #     invoice_place_of_supply: str
# #     invoice_notes: str
# #     invoice_subtotal: float
# #     invoice_total_cgst: float
# #     invoice_total_sgst: float
# #     invoice_total_igst: float # Added for IGST
# #     invoice_total: float
# #     created_at: datetime
# #     invoice_by: Optional[CompanyOut] = None # Use CompanyOut for nested relationship
# #     client: Optional[CustomerOut] = None # Use CustomerOut for nested relationship
# #     products: List[InvoiceItemOut] = [] # Use InvoiceItemOut for nested items

# #     class Config:
# #         from_attributes = True

# # # API Response Models
# # class SingleInvoiceResponse(APIResponse[InvoiceOut]):
# #     """Response model for a single invoice."""
# #     pass

# # class ListInvoiceResponse(APIResponse[List[InvoiceOut]]):
# #     """Response model for a list of invoices."""
# #     pass



# # app/schemas/invoices.py
# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import List, Optional

# from app.schemas.common import APIResponse
# from app.schemas.companies import CompanyOut
# from app.schemas.customers import CustomerOut
# from app.schemas.products import ProductOut # ADD THIS IMPORT
# from app.schemas.invoice_items import InvoiceItemOut # New schema for invoice items output (this will be updated)

# # Schema for creating invoice items within an invoice
# class InvoiceItemInput(BaseModel):
#     product_id: str
#     invoice_item_quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

#     class Config:
#         from_attributes = True

# # Schema for creating a new invoice with items
# class CreateInvoiceWithItems(BaseModel):
#     owner_company: str
#     customer_company: str
#     invoice_number: str
#     invoice_date: datetime
#     invoice_due_date: datetime
#     invoice_terms: str
#     invoice_place_of_supply: str
#     invoice_notes: str
#     invoice_items: List[InvoiceItemInput] = Field(..., description="An invoice must have at least one item.")

#     # New fields for creation
#     invoice_status: str = Field("pending", description="Current status of the invoice (e.g., pending, paid, partially paid).")
#     user_reference_notes: Optional[str] = Field(None, description="Internal notes for user reference, not displayed on invoice.")

#     class Config:
#         from_attributes = True

# # Schema for updating an invoice (allowing partial updates)
# class UpdateInvoice(BaseModel):
#     invoice_number: Optional[str] = None
#     invoice_date: Optional[datetime] = None
#     invoice_due_date: Optional[datetime] = None
#     invoice_terms: Optional[str] = None
#     invoice_place_of_supply: Optional[str] = None
#     invoice_notes: Optional[str] = None

#     # New fields for update
#     invoice_status: Optional[str] = None
#     user_reference_notes: Optional[str] = None

#     class Config:
#         from_attributes = True

# # Output schema for a single invoice item (including calculated fields)
# # This `InvoiceItemOut` here should be replaced with the one from `app/schemas/invoice_items.py` if it's imported correctly.
# # Assuming you have a separate `app/schemas/invoice_items.py` as provided previously.
# # If this is the only place it's defined, then this definition is fine.
# # I'm providing the definition as per the previous `invoice_items.py` content.
# class InvoiceItemOut(BaseModel):
#     invoice_item_id: str
#     invoice_id: str
#     product_id: str
#     invoice_item_quantity: int
#     invoice_item_cgst_rate: float
#     invoice_item_sgst_rate: float
#     invoice_item_igst_rate: float
#     # Calculated fields for output only
#     invoice_item_unit_price: float
#     invoice_item_total_amount_before_tax: float
#     invoice_item_cgst_amount: float
#     invoice_item_sgst_amount: float
#     invoice_item_igst_amount: float
#     invoice_item_total_amount: float
#     created_at: datetime
#     product: Optional[ProductOut] = None # UNCOMMENT THIS LINE

#     class Config:
#         from_attributes = True

# # Output schema for an Invoice
# class InvoiceOut(BaseModel):
#     invoice_id: str
#     owner_company: str
#     customer_company: str
#     invoice_number: str
#     invoice_date: datetime
#     invoice_due_date: datetime
#     invoice_terms: str
#     invoice_place_of_supply: str
#     invoice_notes: str
#     invoice_subtotal: float
#     invoice_total_cgst: float
#     invoice_total_sgst: float
#     invoice_total_igst: float
#     invoice_total: float
#     created_at: datetime

#     # New fields for output
#     invoice_status: str
#     user_reference_notes: Optional[str] = None

#     invoice_by: Optional[CompanyOut] = None
#     client: Optional[CustomerOut] = None
#     products: List[InvoiceItemOut] = []

#     class Config:
#         from_attributes = True

# # API Response Models
# class SingleInvoiceResponse(APIResponse[InvoiceOut]):
#     """Response model for a single invoice."""
#     pass

# class ListInvoiceResponse(APIResponse[List[InvoiceOut]]):
#     """Response model for a list of invoices."""
#     pass

# app/schemas/invoices.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from app.schemas.common import APIResponse
from app.schemas.companies import CompanyOut
from app.schemas.customers import CustomerOut
from app.schemas.products import ProductOut
from app.schemas.invoice_items import InvoiceItemOut

# Schema for creating/updating invoice items within an invoice
class InvoiceItemInput(BaseModel):
    product_id: str
    invoice_item_quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")

    class Config:
        from_attributes = True

# Schema for creating a new invoice with items
class CreateInvoiceWithItems(BaseModel):
    owner_company: str
    customer_company: str
    invoice_number: str
    invoice_date: datetime
    invoice_due_date: datetime
    invoice_terms: str
    invoice_place_of_supply: str
    invoice_notes: str
    invoice_items: List[InvoiceItemInput] = Field(..., description="An invoice must have at least one item.")

    # New fields for creation
    invoice_status: str = Field("pending", description="Current status of the invoice (e.g., pending, paid, partially paid).")
    user_reference_notes: Optional[str] = Field(None, description="Internal notes for user reference, not displayed on invoice.")

    class Config:
        from_attributes = True

# Schema for updating an invoice (allowing partial updates including items)
class UpdateInvoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    invoice_due_date: Optional[datetime] = None
    invoice_terms: Optional[str] = None
    invoice_place_of_supply: Optional[str] = None
    invoice_notes: Optional[str] = None

    # New fields for update
    invoice_status: Optional[str] = None
    user_reference_notes: Optional[str] = None
    
    # Add invoice_items for updating quantities
    invoice_items: Optional[List[InvoiceItemInput]] = Field(None, description="Update invoice items and quantities. If provided, will replace all existing items.")

    class Config:
        from_attributes = True

# Output schema for a single invoice item (including calculated fields)
class InvoiceItemOut(BaseModel):
    invoice_item_id: str
    invoice_id: str
    product_id: str
    invoice_item_quantity: int
    invoice_item_cgst_rate: float
    invoice_item_sgst_rate: float
    invoice_item_igst_rate: float
    # Calculated fields for output only
    invoice_item_unit_price: float
    invoice_item_total_amount_before_tax: float
    invoice_item_cgst_amount: float
    invoice_item_sgst_amount: float
    invoice_item_igst_amount: float
    invoice_item_total_amount: float
    created_at: datetime
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True

# Output schema for an Invoice
class InvoiceOut(BaseModel):
    invoice_id: str
    owner_company: str
    customer_company: str
    invoice_number: str
    invoice_date: datetime
    invoice_due_date: datetime
    invoice_terms: str
    invoice_place_of_supply: str
    invoice_notes: str
    invoice_subtotal: float
    invoice_total_cgst: float
    invoice_total_sgst: float
    invoice_total_igst: float
    invoice_total: float
    created_at: datetime

    # New fields for output
    invoice_status: str
    user_reference_notes: Optional[str] = None

    invoice_by: Optional[CompanyOut] = None
    client: Optional[CustomerOut] = None
    products: List[InvoiceItemOut] = []

    class Config:
        from_attributes = True

# API Response Models
class SingleInvoiceResponse(APIResponse[InvoiceOut]):
    """Response model for a single invoice."""
    pass

class ListInvoiceResponse(APIResponse[List[InvoiceOut]]):
    """Response model for a list of invoices."""
    pass