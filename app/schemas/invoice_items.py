from pydantic import BaseModel
from typing import Optional
from app.schemas.products import CreateProduct

class InvoiceItems(BaseModel):
    invoice_item_quantity: int
    invoice_item_cgst_rate: float
    invoice_item_sgst_rate: float
    invoice_item_cgst_amount: float
    invoice_item_sgst_amount: float
    invoice_item_total: float
    product: Optional[CreateProduct] = []
    
    class Config:
        orm_mode = True