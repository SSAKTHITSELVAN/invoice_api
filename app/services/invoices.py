# app/services/invoices.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, delete
from sqlalchemy.orm import selectinload
from app.models.invoices import Invoices
from app.models.invoice_items import InvoiceItems
from app.models.products import Products
from app.models.companies import Companies
from app.models.customers import Customers
from app.schemas.invoices import CreateInvoiceWithItems, UpdateInvoice, InvoiceItemOut
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Union

# Import dependencies for authentication and company context
from app.services.users import get_current_active_user # Assuming this exists
# from app.services.customers import get_current_company # This is typically handled by a FastAPI Depends in the router, not imported here for direct use.

# Helper function to convert naive datetimes
def _to_naive_datetime(dt_obj: datetime) -> datetime:
    if dt_obj and hasattr(dt_obj, 'tzinfo') and dt_obj.tzinfo is not None:
        return dt_obj.replace(tzinfo=None)
    return dt_obj

async def create_invoice_with_items(
    invoice_data_with_items: CreateInvoiceWithItems,
    db: AsyncSession,
    current_company: Companies # Dependency injected from router
) -> Invoices:
    """
    Create an invoice with associated items, auto-calculating totals,
    and ensuring the invoice belongs to the current user's company.
    """
    invoice_items_input = invoice_data_with_items.invoice_items

    # 1. Verify owner_company matches current_company
    if invoice_data_with_items.owner_company != current_company.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create invoices for your own company."
        )

    # 2. Verify that the customer company exists and belongs to the current company's context (if applicable)
    customer_result = await db.execute(
        select(Customers).where(Customers.customer_id == invoice_data_with_items.customer_company)
    )
    customer = customer_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )

    # Determine if it's an intrastate or interstate transaction
    is_intrastate = (customer.customer_state == current_company.company_state)

    # Prepare invoice data (exclude items from the initial dict creation)
    invoice_dict = invoice_data_with_items.dict(exclude={'invoice_items'})
    invoice_dict['invoice_date'] = _to_naive_datetime(invoice_dict.get('invoice_date'))
    invoice_dict['invoice_due_date'] = _to_naive_datetime(invoice_dict.get('invoice_due_date'))

    # Initialize totals for calculation
    calculated_subtotal = 0.0
    calculated_total_cgst = 0.0
    calculated_total_sgst = 0.0
    calculated_total_igst = 0.0
    new_invoice_items = []

    try:
        # Fetch all products in one go to reduce database roundtrips
        product_ids = [item.product_id for item in invoice_items_input]
        products_result = await db.execute(
            select(Products).where(
                Products.product_id.in_(product_ids),
                Products.company_id == current_company.company_id # Ensure product belongs to the current company
            )
        )
        products_map = {p.product_id: p for p in products_result.scalars().all()}

        if len(products_map) != len(product_ids):
            found_product_ids = set(products_map.keys())
            missing_products = [pid for pid in product_ids if pid not in found_product_ids]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Some products not found or do not belong to your company: {', '.join(missing_products)}"
            )

        for item_input in invoice_items_input:
            product = products_map.get(item_input.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item_input.product_id} not found or does not belong to your company."
                )

            quantity = item_input.invoice_item_quantity
            item_base_total = product.product_unit_price * quantity

            item_cgst_amount = 0.0
            item_sgst_amount = 0.0
            item_igst_amount = 0.0
            item_cgst_rate_to_store = 0.0
            item_sgst_rate_to_store = 0.0
            item_igst_rate_to_store = 0.0

            if is_intrastate:
                item_cgst_rate_to_store = product.product_default_cgst_rate
                item_sgst_rate_to_store = product.product_default_sgst_rate
                item_cgst_amount = (item_base_total * item_cgst_rate_to_store) / 100
                item_sgst_amount = (item_base_total * item_sgst_rate_to_store) / 100
            else:
                item_igst_rate_to_store = product.product_default_igst_rate
                item_igst_amount = (item_base_total * item_igst_rate_to_store) / 100

            new_invoice_item = InvoiceItems(
                product_id=product.product_id,
                invoice_item_quantity=quantity,
                invoice_item_cgst_rate=item_cgst_rate_to_store,
                invoice_item_sgst_rate=item_sgst_rate_to_store,
                invoice_item_igst_rate=item_igst_rate_to_store,
            )
            new_invoice_items.append(new_invoice_item)

            calculated_subtotal += item_base_total
            calculated_total_cgst += item_cgst_amount
            calculated_total_sgst += item_sgst_amount
            calculated_total_igst += item_igst_amount

        # Set calculated totals and new fields on the invoice object
        new_invoice = Invoices(**invoice_dict)
        new_invoice.invoice_subtotal = calculated_subtotal
        new_invoice.invoice_total_cgst = calculated_total_cgst
        new_invoice.invoice_total_sgst = calculated_total_sgst
        new_invoice.invoice_total_igst = calculated_total_igst
        new_invoice.invoice_total = calculated_subtotal + calculated_total_cgst + calculated_total_sgst + calculated_total_igst

        # New fields from CreateInvoiceWithItems
        new_invoice.invoice_status = invoice_data_with_items.invoice_status
        new_invoice.user_reference_notes = invoice_data_with_items.user_reference_notes

        # Add invoice and its items
        db.add(new_invoice)
        await db.flush() # Flush to get new_invoice.invoice_id
        for item in new_invoice_items:
            item.invoice_id = new_invoice.invoice_id
            db.add(item)

        await db.commit()
        await db.refresh(new_invoice)

        # Load relationships for the response
        await db.execute(
            select(Invoices)
            .options(
                selectinload(Invoices.owner_company_rel),
                selectinload(Invoices.client),
                selectinload(Invoices.invoice_items).selectinload(InvoiceItems.product)
            )
            .where(Invoices.invoice_id == new_invoice.invoice_id)
        )
        return new_invoice

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating invoice with items: {str(e)}"
        )

async def show_all_invoices(db: AsyncSession, current_company: Companies) -> List[Invoices]:
    """
    Get all invoices relevant to the current authenticated company
    (either as owner or customer).
    """
    result = await db.execute(
        select(Invoices)
        .options(
            selectinload(Invoices.owner_company_rel),
            selectinload(Invoices.client),
            selectinload(Invoices.invoice_items).selectinload(InvoiceItems.product)
        )
        .where(
            or_(
                Invoices.owner_company == current_company.company_id,
                Invoices.customer_company == current_company.company_id
            )
        )
    )
    invoices = result.scalars().all()
    return invoices

async def get_invoice_by_id(
    invoice_id: str,
    db: AsyncSession,
    current_company: Companies
) -> Invoices:
    """
    Get a specific invoice by ID, ensuring it belongs to or is related to the current company.
    """
    result = await db.execute(
        select(Invoices)
        .options(
            selectinload(Invoices.owner_company_rel),
            selectinload(Invoices.client),
            selectinload(Invoices.invoice_items).selectinload(InvoiceItems.product)
        )
        .where(
            Invoices.invoice_id == invoice_id,
            or_(
                Invoices.owner_company == current_company.company_id,
                Invoices.customer_company == current_company.company_id
            )
        )
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invoice not found or does not belong to your company.'
        )
    return invoice

async def _recalculate_invoice_totals(
    invoice: Invoices, 
    db: AsyncSession, 
    current_company: Companies
) -> None:
    """
    Recalculate invoice totals based on current items.
    """
    # Get customer to determine if intrastate or interstate
    customer_result = await db.execute(
        select(Customers).where(Customers.customer_id == invoice.customer_company)
    )
    customer = customer_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )

    is_intrastate = (customer.customer_state == current_company.company_state)

    # Initialize totals
    calculated_subtotal = 0.0
    calculated_total_cgst = 0.0
    calculated_total_sgst = 0.0
    calculated_total_igst = 0.0

    # Calculate totals from invoice items
    for item in invoice.invoice_items:
        item_base_total = item.product.product_unit_price * item.invoice_item_quantity
        
        if is_intrastate:
            item_cgst_amount = (item_base_total * item.invoice_item_cgst_rate) / 100
            item_sgst_amount = (item_base_total * item.invoice_item_sgst_rate) / 100
            calculated_total_cgst += item_cgst_amount
            calculated_total_sgst += item_sgst_amount
        else:
            item_igst_amount = (item_base_total * item.invoice_item_igst_rate) / 100
            calculated_total_igst += item_igst_amount

        calculated_subtotal += item_base_total

    # Update invoice totals
    invoice.invoice_subtotal = calculated_subtotal
    invoice.invoice_total_cgst = calculated_total_cgst
    invoice.invoice_total_sgst = calculated_total_sgst
    invoice.invoice_total_igst = calculated_total_igst
    invoice.invoice_total = calculated_subtotal + calculated_total_cgst + calculated_total_sgst + calculated_total_igst

async def update_invoice_details(
    invoice_id: str,
    updated_details: UpdateInvoice,
    db: AsyncSession,
    current_company: Companies
) -> Invoices:
    """
    Update an existing invoice's details and optionally its items,
    ensuring it belongs to the current company.
    """
    invoice = await get_invoice_by_id(invoice_id, db, current_company)

    # Verify the invoice belongs to the current company as owner (only owners can update)
    if invoice.owner_company != current_company.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update invoices that your company owns."
        )

    update_data = updated_details.dict(exclude_unset=True, exclude={'invoice_items'})

    # Convert timezone-aware datetimes to naive datetimes for updates
    if 'invoice_date' in update_data:
        update_data['invoice_date'] = _to_naive_datetime(update_data['invoice_date'])
    if 'invoice_due_date' in update_data:
        update_data['invoice_due_date'] = _to_naive_datetime(update_data['invoice_due_date'])

    try:
        # Update invoice header fields
        for key, value in update_data.items():
            setattr(invoice, key, value)

        # Handle invoice items update if provided
        if updated_details.invoice_items is not None:
            # Delete existing items
            await db.execute(
                delete(InvoiceItems).where(InvoiceItems.invoice_id == invoice_id)
            )
            await db.flush()

            # Get customer to determine tax calculation
            customer_result = await db.execute(
                select(Customers).where(Customers.customer_id == invoice.customer_company)
            )
            customer = customer_result.scalar_one_or_none()
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found."
                )

            is_intrastate = (customer.customer_state == current_company.company_state)

            # Fetch all products for the new items
            product_ids = [item.product_id for item in updated_details.invoice_items]
            products_result = await db.execute(
                select(Products).where(
                    Products.product_id.in_(product_ids),
                    Products.company_id == current_company.company_id
                )
            )
            products_map = {p.product_id: p for p in products_result.scalars().all()}

            if len(products_map) != len(product_ids):
                found_product_ids = set(products_map.keys())
                missing_products = [pid for pid in product_ids if pid not in found_product_ids]
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Some products not found or do not belong to your company: {', '.join(missing_products)}"
                )

            # Create new items
            new_invoice_items = []
            for item_input in updated_details.invoice_items:
                product = products_map.get(item_input.product_id)
                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Product with ID {item_input.product_id} not found."
                    )

                # Calculate tax rates based on transaction type
                item_cgst_rate_to_store = 0.0
                item_sgst_rate_to_store = 0.0
                item_igst_rate_to_store = 0.0

                if is_intrastate:
                    item_cgst_rate_to_store = product.product_default_cgst_rate
                    item_sgst_rate_to_store = product.product_default_sgst_rate
                else:
                    item_igst_rate_to_store = product.product_default_igst_rate

                new_invoice_item = InvoiceItems(
                    invoice_id=invoice_id,
                    product_id=product.product_id,
                    invoice_item_quantity=item_input.invoice_item_quantity,
                    invoice_item_cgst_rate=item_cgst_rate_to_store,
                    invoice_item_sgst_rate=item_sgst_rate_to_store,
                    invoice_item_igst_rate=item_igst_rate_to_store,
                )
                new_invoice_items.append(new_invoice_item)
                db.add(new_invoice_item)

            await db.flush()

            # Refresh the invoice to get the new items
            await db.refresh(invoice)

            # Recalculate totals
            await _recalculate_invoice_totals(invoice, db, current_company)

        await db.commit()
        await db.refresh(invoice)
        
        # Load relationships for response
        result = await db.execute(
            select(Invoices)
            .options(
                selectinload(Invoices.owner_company_rel),
                selectinload(Invoices.client),
                selectinload(Invoices.invoice_items).selectinload(InvoiceItems.product)
            )
            .where(Invoices.invoice_id == invoice.invoice_id)
        )
        return result.scalar_one()

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating invoice: {str(e)}"
        )

async def delete_invoice(
    invoice_id: str,
    db: AsyncSession,
    current_company: Companies
) -> dict:
    """
    Delete an invoice and its related items, ensuring it belongs to the current company.
    """
    invoice = await get_invoice_by_id(invoice_id, db, current_company)

    try:
        await db.delete(invoice)
        await db.commit()
        return {"message": "Invoice successfully deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting invoice: {str(e)}"
        )

async def get_invoices_by_specific_company_role(
    company_id_param: str,
    db: AsyncSession,
    current_company: Companies,
    role: str # 'owner' or 'customer'
) -> List[Invoices]:
    """
    Get invoices where the current company plays a specific role (owner or customer).
    Ensures that the company_id_param matches the current_company's ID.
    """
    if company_id_param != current_company.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not authorized to view invoices for company ID {company_id_param}."
        )

    if role == 'owner':
        query_clause = Invoices.owner_company == current_company.company_id
    elif role == 'customer':
        query_clause = Invoices.customer_company == current_company.company_id
    else:
        raise ValueError("Role must be 'owner' or 'customer'")

    result = await db.execute(
        select(Invoices)
        .options(
            selectinload(Invoices.owner_company_rel),
            selectinload(Invoices.client),
            selectinload(Invoices.invoice_items).selectinload(InvoiceItems.product)
        )
        .where(query_clause)
    )
    invoices = result.scalars().all()
    return invoices