
# app/api/routers/invoices.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.invoices import (
    CreateInvoiceWithItems,
    UpdateInvoice,
    InvoiceOut,
    SingleInvoiceResponse,
    ListInvoiceResponse,
    InvoiceItemOut # For consistent item output
)
from app.schemas.common import APIResponse # Assuming this exists
from app.services import invoices as invoice_service
from app.services.users import get_current_active_user # For user authentication
from app.services.customers import get_current_company # Corrected import for company context
from app.models.users import Users
from app.models.companies import Companies

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/", response_model=SingleInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice_endpoint(
    invoice_data_with_items: CreateInvoiceWithItems,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user), # Authenticate user
    current_company: Companies = Depends(get_current_company) # Get current company
):
    """
    Create a new invoice along with its items.
    The invoice owner_company must match the authenticated user's current company.
    """
    new_invoice = await invoice_service.create_invoice_with_items(
        invoice_data_with_items, db, current_company
    )

    # Prepare InvoiceItemOut objects for the response
    products_out_list = []
    for item in new_invoice.invoice_items: # Corrected from .products
        item_base_total = item.product.product_unit_price * item.invoice_item_quantity
        item_cgst_amount = item_base_total * (item.invoice_item_cgst_rate / 100)
        item_sgst_amount = item_base_total * (item.invoice_item_sgst_rate / 100)
        item_igst_amount = item_base_total * (item.invoice_item_igst_rate / 100)
        item_total_amount = item_base_total + item_cgst_amount + item_sgst_amount + item_igst_amount

        products_out_list.append(
            InvoiceItemOut(
                invoice_item_id=str(item.invoice_item_id),
                invoice_id=str(item.invoice_id),
                product_id=str(item.product_id),
                invoice_item_quantity=item.invoice_item_quantity,
                invoice_item_cgst_rate=item.invoice_item_cgst_rate,
                invoice_item_sgst_rate=item.invoice_item_sgst_rate,
                invoice_item_igst_rate=item.invoice_item_igst_rate,
                invoice_item_unit_price=item.product.product_unit_price, # Add unit price
                invoice_item_total_amount_before_tax=item_base_total,
                invoice_item_cgst_amount=item_cgst_amount,
                invoice_item_sgst_amount=item_sgst_amount,
                invoice_item_igst_amount=item_igst_amount,
                invoice_item_total_amount=item_total_amount,
                created_at=item.created_at,
                # product=ProductOut.model_validate(item.product) # If ProductOut is needed here
            )
        )

    return SingleInvoiceResponse(
        status_code=status.HTTP_201_CREATED,
        message="Invoice created successfully",
        data=InvoiceOut(
            invoice_id=str(new_invoice.invoice_id),
            owner_company=str(new_invoice.owner_company),
            customer_company=str(new_invoice.customer_company),
            invoice_number=new_invoice.invoice_number,
            invoice_date=new_invoice.invoice_date,
            invoice_due_date=new_invoice.invoice_due_date,
            invoice_terms=new_invoice.invoice_terms,
            invoice_place_of_supply=new_invoice.invoice_place_of_supply,
            invoice_notes=new_invoice.invoice_notes,
            invoice_subtotal=new_invoice.invoice_subtotal,
            invoice_total_cgst=new_invoice.invoice_total_cgst,
            invoice_total_sgst=new_invoice.invoice_total_sgst,
            invoice_total_igst=new_invoice.invoice_total_igst,
            invoice_total=new_invoice.invoice_total,
            invoice_status=new_invoice.invoice_status, # Added invoice_status
            created_at=new_invoice.created_at,
            invoice_by=new_invoice.owner_company_rel, # Corrected
            client=new_invoice.client,
            products=products_out_list
        )
    )

@router.get("/", response_model=ListInvoiceResponse)
async def get_all_invoices_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Get all invoices relevant to the authenticated user's company (owner or customer).
    """
    invoices = await invoice_service.show_all_invoices(db, current_company)

    invoices_out_list = []
    for invoice in invoices:
        products_out_list = []
        for item in invoice.invoice_items:
            item_base_total = item.product.product_unit_price * item.invoice_item_quantity
            item_cgst_amount = item_base_total * (item.invoice_item_cgst_rate / 100)
            item_sgst_amount = item_base_total * (item.invoice_item_sgst_rate / 100)
            item_igst_amount = item_base_total * (item.invoice_item_igst_rate / 100)
            item_total_amount = item_base_total + item_cgst_amount + item_sgst_amount + item_igst_amount

            products_out_list.append(
                InvoiceItemOut(
                    invoice_item_id=str(item.invoice_item_id),
                    invoice_id=str(item.invoice_id),
                    product_id=str(item.product_id),
                    invoice_item_quantity=item.invoice_item_quantity,
                    invoice_item_cgst_rate=item.invoice_item_cgst_rate,
                    invoice_item_sgst_rate=item.invoice_item_sgst_rate,
                    invoice_item_igst_rate=item.invoice_item_igst_rate,
                    invoice_item_unit_price=item.product.product_unit_price,
                    invoice_item_total_amount_before_tax=item_base_total,
                    invoice_item_cgst_amount=item_cgst_amount,
                    invoice_item_sgst_amount=item_sgst_amount,
                    invoice_item_igst_amount=item_igst_amount,
                    invoice_item_total_amount=item_total_amount,
                    created_at=item.created_at,
                    # product=ProductOut.model_validate(item.product)
                )
            )
        invoices_out_list.append(
            InvoiceOut(
                invoice_id=str(invoice.invoice_id),
                owner_company=str(invoice.owner_company),
                customer_company=str(invoice.customer_company),
                invoice_number=invoice.invoice_number,
                invoice_date=invoice.invoice_date,
                invoice_due_date=invoice.invoice_due_date,
                invoice_terms=invoice.invoice_terms,
                invoice_place_of_supply=invoice.invoice_place_of_supply,
                invoice_notes=invoice.invoice_notes,
                invoice_subtotal=invoice.invoice_subtotal,
                invoice_total_cgst=invoice.invoice_total_cgst,
                invoice_total_sgst=invoice.invoice_total_sgst,
                invoice_total_igst=invoice.invoice_total_igst,
                invoice_total=invoice.invoice_total,
                invoice_status=invoice.invoice_status, # Added invoice_status
                created_at=invoice.created_at,
                invoice_by=invoice.owner_company_rel, # Corrected
                client=invoice.client,
                products=products_out_list
            )
        )

    return ListInvoiceResponse(
        status_code=status.HTTP_200_OK,
        message="Invoices retrieved successfully",
        data=invoices_out_list
    )

@router.get("/{invoice_id}", response_model=SingleInvoiceResponse)
async def get_invoice_endpoint(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """Get a specific invoice by ID, ensuring it belongs to or is related to your company."""
    invoice = await invoice_service.get_invoice_by_id(invoice_id, db, current_company)

    products_out_list = []
    for item in invoice.invoice_items:
        item_base_total = item.product.product_unit_price * item.invoice_item_quantity
        item_cgst_amount = item_base_total * (item.invoice_item_cgst_rate / 100)
        item_sgst_amount = item_base_total * (item.invoice_item_sgst_rate / 100)
        item_igst_amount = item_base_total * (item.invoice_item_igst_rate / 100)
        item_total_amount = item_base_total + item_cgst_amount + item_sgst_amount + item_igst_amount

        products_out_list.append(
            InvoiceItemOut(
                invoice_item_id=str(item.invoice_item_id),
                invoice_id=str(item.invoice_id),
                product_id=str(item.product_id),
                invoice_item_quantity=item.invoice_item_quantity,
                invoice_item_cgst_rate=item.invoice_item_cgst_rate,
                invoice_item_sgst_rate=item.invoice_item_sgst_rate,
                invoice_item_igst_rate=item.invoice_item_igst_rate,
                invoice_item_unit_price=item.product.product_unit_price,
                invoice_item_total_amount_before_tax=item_base_total,
                invoice_item_cgst_amount=item_cgst_amount,
                invoice_item_sgst_amount=item_sgst_amount,
                invoice_item_igst_amount=item_igst_amount,
                invoice_item_total_amount=item_total_amount,
                created_at=item.created_at,
                # product=ProductOut.model_validate(item.product)
            )
        )

    return SingleInvoiceResponse(
        status_code=status.HTTP_200_OK,
        message="Invoice retrieved successfully",
        data=InvoiceOut(
            invoice_id=str(invoice.invoice_id),
            owner_company=str(invoice.owner_company),
            customer_company=str(invoice.customer_company),
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            invoice_due_date=invoice.invoice_due_date,
            invoice_terms=invoice.invoice_terms,
            invoice_place_of_supply=invoice.invoice_place_of_supply,
            invoice_notes=invoice.invoice_notes,
            invoice_subtotal=invoice.invoice_subtotal,
            invoice_total_cgst=invoice.invoice_total_cgst,
            invoice_total_sgst=invoice.invoice_total_sgst,
            invoice_total_igst=invoice.invoice_total_igst,
            invoice_total=invoice.invoice_total,
            invoice_status=invoice.invoice_status, # Added invoice_status
            created_at=invoice.created_at,
            invoice_by=invoice.owner_company_rel, # Corrected
            client=invoice.client,
            products=products_out_list
        )
    )

@router.put("/{invoice_id}", response_model=SingleInvoiceResponse)
async def update_invoice_endpoint(
    invoice_id: str,
    updated_details: UpdateInvoice,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """Update an existing invoice's header details, ensuring it belongs to your company."""
    invoice = await invoice_service.update_invoice_details(
        invoice_id, updated_details, db, current_company
    )

    products_out_list = []
    for item in invoice.invoice_items:
        item_base_total = item.product.product_unit_price * item.invoice_item_quantity
        item_cgst_amount = item_base_total * (item.invoice_item_cgst_rate / 100)
        item_sgst_amount = item_base_total * (item.invoice_item_sgst_rate / 100)
        item_igst_amount = item_base_total * (item.invoice_item_igst_rate / 100)
        item_total_amount = item_base_total + item_cgst_amount + item_sgst_amount + item_igst_amount

        products_out_list.append(
            InvoiceItemOut(
                invoice_item_id=str(item.invoice_item_id),
                invoice_id=str(item.invoice_id),
                product_id=str(item.product_id),
                invoice_item_quantity=item.invoice_item_quantity,
                invoice_item_cgst_rate=item.invoice_item_cgst_rate,
                invoice_item_sgst_rate=item.invoice_item_sgst_rate,
                invoice_item_igst_rate=item.invoice_item_igst_rate,
                invoice_item_unit_price=item.product.product_unit_price,
                invoice_item_total_amount_before_tax=item_base_total,
                invoice_item_cgst_amount=item_cgst_amount,
                invoice_item_sgst_amount=item_sgst_amount,
                invoice_item_igst_amount=item_igst_amount,
                invoice_item_total_amount=item_total_amount,
                created_at=item.created_at,
                # product=ProductOut.model_validate(item.product)
            )
        )

    return SingleInvoiceResponse(
        status_code=status.HTTP_200_OK,
        message="Invoice updated successfully",
        data=InvoiceOut(
            invoice_id=str(invoice.invoice_id),
            owner_company=str(invoice.owner_company),
            customer_company=str(invoice.customer_company),
            invoice_number=invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            invoice_due_date=invoice.invoice_due_date,
            invoice_terms=invoice.invoice_terms,
            invoice_place_of_supply=invoice.invoice_place_of_supply,
            invoice_notes=invoice.invoice_notes,
            invoice_subtotal=invoice.invoice_subtotal,
            invoice_total_cgst=invoice.invoice_total_cgst,
            invoice_total_sgst=invoice.invoice_total_sgst,
            invoice_total_igst=invoice.invoice_total_igst,
            invoice_total=invoice.invoice_total,
            invoice_status=invoice.invoice_status, # Added invoice_status
            created_at=invoice.created_at,
            invoice_by=invoice.owner_company_rel, # Corrected
            client=invoice.client,
            products=products_out_list
        )
    )

@router.delete("/{invoice_id}", response_model=APIResponse[None])
async def delete_invoice_endpoint(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """Delete an invoice and its associated items, ensuring it belongs to your company."""
    await invoice_service.delete_invoice(invoice_id, db, current_company)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Invoice successfully deleted",
        data=None
    )

@router.get("/company/{company_id_param}", response_model=ListInvoiceResponse)
async def get_invoices_by_owner_company_endpoint(
    company_id_param: str,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Get all invoices where the authenticated company is the owner.
    `company_id_param` must match the authenticated user's `current_company.company_id`.
    """
    invoices = await invoice_service.get_invoices_by_specific_company_role(
        company_id_param, db, current_company, 'owner'
    )

    invoices_out_list = []
    for invoice in invoices:
        products_out_list = []
        for item in invoice.invoice_items:
            item_base_total = item.product.product_unit_price * item.invoice_item_quantity
            item_cgst_amount = item_base_total * (item.invoice_item_cgst_rate / 100)
            item_sgst_amount = item_base_total * (item.invoice_item_sgst_rate / 100)
            item_igst_amount = item_base_total * (item.invoice_item_igst_rate / 100)
            item_total_amount = item_base_total + item_cgst_amount + item_sgst_amount + item_igst_amount

            products_out_list.append(
                InvoiceItemOut(
                    invoice_item_id=str(item.invoice_item_id),
                    invoice_id=str(item.invoice_id),
                    product_id=str(item.product_id),
                    invoice_item_quantity=item.invoice_item_quantity,
                    invoice_item_cgst_rate=item.invoice_item_cgst_rate,
                    invoice_item_sgst_rate=item.invoice_item_sgst_rate,
                    invoice_item_igst_rate=item.invoice_item_igst_rate,
                    invoice_item_unit_price=item.product.product_unit_price,
                    invoice_item_total_amount_before_tax=item_base_total,
                    invoice_item_cgst_amount=item_cgst_amount,
                    invoice_item_sgst_amount=item_sgst_amount,
                    invoice_item_igst_amount=item_igst_amount,
                    invoice_item_total_amount=item_total_amount,
                    created_at=item.created_at,
                    # product=ProductOut.model_validate(item.product)
                )
            )
        invoices_out_list.append(
            InvoiceOut(
                invoice_id=str(invoice.invoice_id),
                owner_company=str(invoice.owner_company),
                customer_company=str(invoice.customer_company),
                invoice_number=invoice.invoice_number,
                invoice_date=invoice.invoice_date,
                invoice_due_date=invoice.invoice_due_date,
                invoice_terms=invoice.invoice_terms,
                invoice_place_of_supply=invoice.invoice_place_of_supply,
                invoice_notes=invoice.invoice_notes,
                invoice_subtotal=invoice.invoice_subtotal,
                invoice_total_cgst=invoice.invoice_total_cgst,
                invoice_total_sgst=invoice.invoice_total_sgst,
                invoice_total_igst=invoice.invoice_total_igst,
                invoice_total=invoice.invoice_total,
                invoice_status=invoice.invoice_status, # Added invoice_status
                created_at=invoice.created_at,
                invoice_by=invoice.owner_company_rel, # Corrected
                client=invoice.client,
                products=products_out_list
            )
        )
    return ListInvoiceResponse(
        status_code=status.HTTP_200_OK,
        message="Invoices by owner company retrieved successfully",
        data=invoices_out_list
    )

@router.get("/customer/{customer_id_param}", response_model=ListInvoiceResponse)
async def get_invoices_by_customer_company_endpoint(
    customer_id_param: str, # Changed to str for UUID
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Get all invoices where the authenticated company is the customer.
    `customer_id_param` must match the authenticated user's `current_company.company_id`.
    """
    # This endpoint specifically for when the current company IS the customer.
    # The `customer_id_param` is just a placeholder, the actual filtering happens by `current_company.company_id`
    if customer_id_param != current_company.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not authorized to view invoices for customer ID {customer_id_param}."
        )

    invoices = await invoice_service.get_invoices_by_specific_company_role(
        current_company.company_id, db, current_company, 'customer'
    )

    invoices_out_list = []
    for invoice in invoices:
        products_out_list = []
        for item in invoice.invoice_items:
            item_base_total = item.product.product_unit_price * item.invoice_item_quantity
            item_cgst_amount = item_base_total * (item.invoice_item_cgst_rate / 100)
            item_sgst_amount = item_base_total * (item.invoice_item_sgst_rate / 100)
            item_igst_amount = item_base_total * (item.invoice_item_igst_rate / 100)
            item_total_amount = item_base_total + item_cgst_amount + item_sgst_amount + item_igst_amount

            products_out_list.append(
                InvoiceItemOut(
                    invoice_item_id=str(item.invoice_item_id),
                    invoice_id=str(item.invoice_id),
                    product_id=str(item.product_id),
                    invoice_item_quantity=item.invoice_item_quantity,
                    invoice_item_cgst_rate=item.invoice_item_cgst_rate,
                    invoice_item_sgst_rate=item.invoice_item_sgst_rate,
                    invoice_item_igst_rate=item.invoice_item_igst_rate,
                    invoice_item_unit_price=item.product.product_unit_price,
                    invoice_item_total_amount_before_tax=item_base_total,
                    invoice_item_cgst_amount=item_cgst_amount,
                    invoice_item_sgst_amount=item_sgst_amount,
                    invoice_item_igst_amount=item_igst_amount,
                    invoice_item_total_amount=item_total_amount,
                    created_at=item.created_at,
                    # product=ProductOut.model_validate(item.product)
                )
            )
        invoices_out_list.append(
            InvoiceOut(
                invoice_id=str(invoice.invoice_id),
                owner_company=str(invoice.owner_company),
                customer_company=str(invoice.customer_company),
                invoice_number=invoice.invoice_number,
                invoice_date=invoice.invoice_date,
                invoice_due_date=invoice.invoice_due_date,
                invoice_terms=invoice.invoice_terms,
                invoice_place_of_supply=invoice.invoice_place_of_supply,
                invoice_notes=invoice.invoice_notes,
                invoice_subtotal=invoice.invoice_subtotal,
                invoice_total_cgst=invoice.invoice_total_cgst,
                invoice_total_sgst=invoice.invoice_total_sgst,
                invoice_total_igst=invoice.invoice_total_igst,
                invoice_total=invoice.invoice_total,
                invoice_status=invoice.invoice_status, # Added invoice_status
                created_at=invoice.created_at,
                invoice_by=invoice.owner_company_rel, # Corrected
                client=invoice.client,
                products=products_out_list
            )
        )
    return ListInvoiceResponse(
        status_code=status.HTTP_200_OK,
        message="Invoices where your company is the customer retrieved successfully",
        data=invoices_out_list
    )