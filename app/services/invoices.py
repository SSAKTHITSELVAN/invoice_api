# ============================================================================
# SERVICES - invoices.py (Updated with full CRUD)
# ============================================================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.invoices import Invoices
from app.models.invoice_items import InvoiceItems
from app.models.products import Products
from app.models.companies import Companies
from app.models.customers import Customers
from app.schemas.invoices import CreateInvoice, UpdateInvoice, CreateInvoiceWithItems
from fastapi import HTTPException, status
from datetime import datetime

async def create_invoice(invoice_data: CreateInvoice, db: AsyncSession):
    """Create a new invoice"""
    try:
        # Verify that the company and customer exist
        company_result = await db.execute(
            select(Companies).where(Companies.company_id == invoice_data.owner_company)
        )
        company = company_result.scalar_one_or_none()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Owner company not found"
            )
        
        customer_result = await db.execute(
            select(Customers).where(Customers.customer_id == invoice_data.customer_company)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Customer not found"
            )
        
        # Convert timezone-aware datetimes to naive datetimes
        invoice_dict = invoice_data.dict()
        if invoice_dict.get('invoice_date') and hasattr(invoice_dict['invoice_date'], 'tzinfo') and invoice_dict['invoice_date'].tzinfo:
            invoice_dict['invoice_date'] = invoice_dict['invoice_date'].replace(tzinfo=None)
        if invoice_dict.get('invoice_due_date') and hasattr(invoice_dict['invoice_due_date'], 'tzinfo') and invoice_dict['invoice_due_date'].tzinfo:
            invoice_dict['invoice_due_date'] = invoice_dict['invoice_due_date'].replace(tzinfo=None)
        
        new_invoice = Invoices(**invoice_dict)
        db.add(new_invoice)
        await db.commit()
        await db.refresh(new_invoice)
        return new_invoice
    
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error creating invoice: {str(e)}"
        )


async def create_invoice_with_items(invoice_with_items: CreateInvoiceWithItems, db: AsyncSession):
    """Create invoice with items in a single transaction"""
    try:
        # Verify that the company and customer exist first
        company_result = await db.execute(
            select(Companies).where(Companies.company_id == invoice_with_items.invoice_data.owner_company)
        )
        company = company_result.scalar_one_or_none()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Owner company not found"
            )
        
        customer_result = await db.execute(
            select(Customers).where(Customers.customer_id == invoice_with_items.invoice_data.customer_company)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Customer not found"
            )
        
        # Convert timezone-aware datetimes to naive datetimes in invoice_data
        invoice_dict = invoice_with_items.invoice_data.dict()
        
        # Safe datetime conversion with type checking
        for field in ['invoice_date', 'invoice_due_date']:
            if (invoice_dict.get(field) and 
                isinstance(invoice_dict[field], datetime) and 
                hasattr(invoice_dict[field], 'tzinfo') and 
                invoice_dict[field].tzinfo):
                invoice_dict[field] = invoice_dict[field].replace(tzinfo=None)
        
        # Create the invoice
        new_invoice = Invoices(**invoice_dict)
        db.add(new_invoice)
        await db.flush()  # Flush to get the invoice_id without committing
        
        # Add invoice items
        total_cgst = 0
        total_sgst = 0
        subtotal = 0
        
        for item_data in invoice_with_items.invoice_items:
            product_id = item_data.product_id
            quantity = item_data.quantity if item_data.quantity != 0 else 0
            
            # Get product details
            product_result = await db.execute(
                select(Products).where(Products.product_id == product_id)
            )
            product = product_result.scalar_one_or_none()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )
            
            # Calculate amounts
            item_total = product.product_unit_price * quantity
            cgst_amount = item_total * (product.product_default_cgst_rate / 100)
            sgst_amount = item_total * (product.product_default_sgst_rate / 100)
            
            # Create invoice item
            invoice_item = InvoiceItems(
                invoice_id=new_invoice.invoice_id,
                product_id=product_id,
                invoice_item_quantity=quantity,
                invoice_item_cgst_rate=product.product_default_cgst_rate,
                invoice_item_sgst_rate=product.product_default_sgst_rate,
                invoice_item_cgst_amount=cgst_amount,
                invoice_item_sgst_amount=sgst_amount,
                invoice_item_total=item_total + cgst_amount + sgst_amount
            )
            
            db.add(invoice_item)
            
            # Update totals
            subtotal += item_total
            total_cgst += cgst_amount
            total_sgst += sgst_amount
        
        # Update invoice totals
        new_invoice.invoice_subtotal = subtotal
        new_invoice.invoice_total_cgst = total_cgst
        new_invoice.invoice_total_sgst = total_sgst
        new_invoice.invoice_total = subtotal + total_cgst + total_sgst
        
        # Commit the transaction
        await db.commit()
        
        # Fetch the complete invoice with relationships
        result = await db.execute(
            select(Invoices).where(Invoices.invoice_id == new_invoice.invoice_id)
        )
        db_invoice = result.scalar_one_or_none()
        
        # Check if invoice was found after commit
        if not db_invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found after creation"
            )
        
        return db_invoice
        
    except HTTPException:
        # Rollback on HTTP exceptions and re-raise
        await db.rollback()
        raise
    except Exception as e:
        # Rollback on any other exception
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating invoice with items: {str(e)}"
        )

async def show_all_invoices(db: AsyncSession):
    """Get all invoices with related data"""
    result = await db.execute(
        select(Invoices)
        .options(
            selectinload(Invoices.invoice_by),
            selectinload(Invoices.client),
            selectinload(Invoices.products).selectinload(InvoiceItems.product)
        )
    )
    invoices = result.scalars().all()
    return invoices

async def show_invoice(invoice_id: int, db: AsyncSession):
    """Get a specific invoice by ID with all related data"""
    result = await db.execute(
        select(Invoices)
        .options(
            selectinload(Invoices.invoice_by),
            selectinload(Invoices.client),
            selectinload(Invoices.products).selectinload(InvoiceItems.product)
        )
        .where(Invoices.invoice_id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Specified invoice is not present...'
        )
    return invoice

async def update_invoice(invoice_id: int, updated_details: UpdateInvoice, db: AsyncSession):
    """Update an existing invoice"""
    try:
        result = await db.execute(select(Invoices).where(Invoices.invoice_id == invoice_id))
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Invoice not found"
            )
        
        updated_data = updated_details.dict(exclude_unset=True)
        
        # Verify company and customer if they are being updated
        if 'owner_company' in updated_data:
            company_result = await db.execute(
                select(Companies).where(Companies.company_id == updated_data['owner_company'])
            )
            if not company_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Owner company not found"
                )
        
        if 'customer_company' in updated_data:
            customer_result = await db.execute(
                select(Customers).where(Customers.customer_id == updated_data['customer_company'])
            )
            if not customer_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found"
                )
        
        # Handle datetime conversion for updates
        if 'invoice_date' in updated_data and updated_data['invoice_date'] and hasattr(updated_data['invoice_date'], 'tzinfo') and updated_data['invoice_date'].tzinfo:
            updated_data['invoice_date'] = updated_data['invoice_date'].replace(tzinfo=None)
        if 'invoice_due_date' in updated_data and updated_data['invoice_due_date'] and hasattr(updated_data['invoice_due_date'], 'tzinfo') and updated_data['invoice_due_date'].tzinfo:
            updated_data['invoice_due_date'] = updated_data['invoice_due_date'].replace(tzinfo=None)
        
        for key, value in updated_data.items():
            setattr(invoice, key, value)
        
        await db.commit()
        await db.refresh(invoice)
        return invoice
    
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating invoice: {str(e)}"
        )

async def delete_invoice(invoice_id: int, db: AsyncSession):
    """Delete an invoice and its related items"""
    try:
        result = await db.execute(select(Invoices).where(Invoices.invoice_id == invoice_id))
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Invoice not found"
            )
        
        await db.delete(invoice)
        await db.commit()
        return {"message": "Invoice successfully deleted"}
    
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting invoice: {str(e)}"
        )

async def get_invoices_by_company(company_id: int, db: AsyncSession):
    """Get all invoices for a specific company"""
    result = await db.execute(
        select(Invoices)
        .options(
            selectinload(Invoices.invoice_by),
            selectinload(Invoices.client),
            selectinload(Invoices.products).selectinload(InvoiceItems.product)
        )
        .where(Invoices.owner_company == company_id)
    )
    invoices = result.scalars().all()
    return invoices

async def get_invoices_by_customer(customer_id: int, db: AsyncSession):
    """Get all invoices for a specific customer"""
    result = await db.execute(
        select(Invoices)
        .options(
            selectinload(Invoices.invoice_by),
            selectinload(Invoices.client),
            selectinload(Invoices.products).selectinload(InvoiceItems.product)
        )
        .where(Invoices.customer_company == customer_id)
    )
    invoices = result.scalars().all()
    return invoices
