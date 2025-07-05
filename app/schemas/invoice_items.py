# app/schemas/invoice_items.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Assuming app.schemas.products exists and has ProductOut
from app.schemas.products import ProductOut

class InvoiceItemOut(BaseModel):
    invoice_item_id: str
    invoice_id: str
    product_id: str
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
    product: Optional[ProductOut] = None # UNCOMMENT THIS LINE

    class Config:
        from_attributes = True