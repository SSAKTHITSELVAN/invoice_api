
# ============================================================================
# ENDPOINTS - Invoice Router
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.invoices import CreateInvoice, UpdateInvoice, InvoiceOut, CreateInvoiceWithItems
from app.services import invoices as invoice_service

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: CreateInvoice, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new invoice"""
    return await invoice_service.create_invoice(invoice, db)

@router.post("/with-items", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
async def create_invoice_with_items(
    invoice_with_items: CreateInvoiceWithItems,
    db: AsyncSession = Depends(get_db)
):
    """Create a new invoice with items in a single transaction"""
    return await invoice_service.create_invoice_with_items(invoice_with_items, db)

@router.get("/", response_model=List[InvoiceOut])
async def get_all_invoices(db: AsyncSession = Depends(get_db)):
    """Get all invoices"""
    return await invoice_service.show_all_invoices(db)

@router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific invoice by ID"""
    return await invoice_service.show_invoice(invoice_id, db)

@router.put("/{invoice_id}", response_model=InvoiceOut)
async def update_invoice(
    invoice_id: int, 
    updated_details: UpdateInvoice, 
    db: AsyncSession = Depends(get_db)
):
    """Update an existing invoice"""
    return await invoice_service.update_invoice(invoice_id, updated_details, db)

@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an invoice"""
    return await invoice_service.delete_invoice(invoice_id, db)

@router.get("/company/{company_id}", response_model=List[InvoiceOut])
async def get_invoices_by_company(
    company_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get all invoices for a specific company"""
    return await invoice_service.get_invoices_by_company(company_id, db)

@router.get("/customer/{customer_id}", response_model=List[InvoiceOut])
async def get_invoices_by_customer(
    customer_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get all invoices for a specific customer"""
    return await invoice_service.get_invoices_by_customer(customer_id, db)
