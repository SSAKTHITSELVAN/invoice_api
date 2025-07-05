# app/api/routers/customers.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.customers import CreateCustomer, UpdateCustomer, CustomerOut, SingleCustomerResponse, ListCustomerResponse
from app.schemas.common import APIResponse # Import APIResponse
from app.services.customers import list_all_customers, create_new_customer, modify_customer_details, remove_customer, get_customer_by_id, get_current_company # Import new services and dependency
from app.services.users import get_current_active_user # Import user authentication
from app.models.users import Users
from app.models.companies import Companies # Import Companies model

# Define the router here. Do not import from app.api.router.customers
router = APIRouter(prefix="/companies/{company_id}/customers", tags=["Customers"])


@router.get("/", response_model=ListCustomerResponse)
async def show_customers_endpoint(
    company_id: str, # To be used by get_current_company dependency
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user), # Authenticate user
    current_company: Companies = Depends(get_current_company) # Authenticate and get company
):
    """
    List all customers for a specific company owned by the authenticated user.
    """
    customers = await list_all_customers(db, current_company)
    customer_out_list = [
        CustomerOut(
            customer_id=str(c.customer_id),
            customer_to=str(c.customer_to),
            customer_name=c.customer_name,
            customer_address_line1=c.customer_address_line1,
            customer_address_line2=c.customer_address_line2,
            customer_city=c.customer_city,
            customer_state=c.customer_state,
            customer_postal_code=c.customer_postal_code,
            customer_country=c.customer_country,
            customer_gstin=c.customer_gstin,
            customer_email=c.customer_email,
            customer_phone=c.customer_phone,
            created_at=c.created_at
        ) for c in customers
    ]
    return ListCustomerResponse(
        status_code=status.HTTP_200_OK,
        message="Customers retrieved successfully",
        data=customer_out_list
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SingleCustomerResponse)
async def add_new_customer_endpoint(
    company_id: str, # To be used by get_current_company dependency
    customer_data: CreateCustomer, # Renamed for clarity
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user), # Authenticate user
    current_company: Companies = Depends(get_current_company) # Authenticate and get company
):
    """
    Add a new customer to a specific company owned by the authenticated user.
    """
    # Ensure the customer_to field matches the company_id from the path
    if customer_data.customer_to != company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="customer_to in request body must match company_id in path."
        )

    new_customer = await create_new_customer(customer_data, db, current_company)
    return SingleCustomerResponse(
        status_code=status.HTTP_201_CREATED,
        message="Customer added successfully",
        data=CustomerOut(
            customer_id=str(new_customer.customer_id),
            customer_to=str(new_customer.customer_to),
            customer_name=new_customer.customer_name,
            customer_address_line1=new_customer.customer_address_line1,
            customer_address_line2=new_customer.customer_address_line2,
            customer_city=new_customer.customer_city,
            customer_state=new_customer.customer_state,
            customer_postal_code=new_customer.customer_postal_code,
            customer_country=new_customer.customer_country,
            customer_gstin=new_customer.customer_gstin,
            customer_email=new_customer.customer_email,
            customer_phone=new_customer.customer_phone,
            created_at=new_customer.created_at
        )
    )

@router.get("/{customer_id}", response_model=SingleCustomerResponse)
async def get_single_customer_endpoint(
    company_id: str,
    customer_id: str, # Changed to str for UUID
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Retrieve a single customer by ID for a specific company.
    """
    customer = await get_customer_by_id(customer_id, db, current_company)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return SingleCustomerResponse(
        status_code=status.HTTP_200_OK,
        message="Customer retrieved successfully",
        data=CustomerOut(
            customer_id=str(customer.customer_id),
            customer_to=str(customer.customer_to),
            customer_name=customer.customer_name,
            customer_address_line1=customer.customer_address_line1,
            customer_address_line2=customer.customer_address_line2,
            customer_city=customer.customer_city,
            customer_state=customer.customer_state,
            customer_postal_code=customer.customer_postal_code,
            customer_country=customer.customer_country,
            customer_gstin=customer.customer_gstin,
            customer_email=customer.customer_email,
            customer_phone=customer.customer_phone,
            created_at=customer.created_at
        )
    )

@router.put("/{customer_id}", response_model=SingleCustomerResponse)
async def update_customer_endpoint(
    company_id: str,
    customer_id: str, # Changed to str for UUID
    updated_customer_data: UpdateCustomer, # Renamed for clarity
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Update details of an existing customer for a specific company.
    """
    customer = await modify_customer_details(customer_id, updated_customer_data, db, current_company)
    return SingleCustomerResponse(
        status_code=status.HTTP_200_OK,
        message="Customer updated successfully",
        data=CustomerOut(
            customer_id=str(customer.customer_id),
            customer_to=str(customer.customer_to),
            customer_name=customer.customer_name,
            customer_address_line1=customer.customer_address_line1,
            customer_address_line2=customer.customer_address_line2,
            customer_city=customer.customer_city,
            customer_state=customer.customer_state,
            customer_postal_code=customer.customer_postal_code,
            customer_country=customer.customer_country,
            customer_gstin=customer.customer_gstin,
            customer_email=customer.customer_email,
            customer_phone=customer.customer_phone,
            created_at=customer.created_at
        )
    )

@router.delete("/{customer_id}", status_code=status.HTTP_200_OK, response_model=APIResponse[None])
async def delete_customer_endpoint(
    company_id: str,
    customer_id: str, # Changed to str for UUID
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Delete a customer for a specific company.
    """
    await remove_customer(customer_id, db, current_company)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Customer successfully deleted",
        data=None
    )