# app/services/customers.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from sqlalchemy import select, delete, update
from app.models.customers import Customers
from app.schemas.customers import CreateCustomer, UpdateCustomer, CustomerOut
from app.services.users import get_current_active_user # For authentication
from app.models.users import Users
from app.models.companies import Companies # Import Companies model
from app.services.companies import get_company_by_id as get_company_by_id_service # Import the service function
from typing import List
from app.database import get_db

# Dependency to get the current company the user is managing
async def get_current_company(
    company_id: str, # This ID would typically come from a path parameter or header
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user)
) -> Companies:
    """
    Dependency to get the company specified by company_id,
    and verify that it belongs to the current authenticated user.
    """
    company = await get_company_by_id_service(company_id, db, current_user)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found or you don't have access to it."
        )
    return company

async def list_all_customers(db: AsyncSession, current_company: Companies) -> List[Customers]:
    """
    Service function to list all customers belonging to a specific company,
    which is owned by the current user.
    """
    result = await db.execute(
        select(Customers).where(Customers.customer_to == current_company.company_id)
    )
    customers = result.scalars().all()
    return customers

async def create_new_customer(
    customer_data: CreateCustomer, # Renamed parameter for clarity
    db: AsyncSession,
    current_company: Companies # Pass the validated company
) -> Customers:
    """
    Service function to create a new customer, ensuring it's for the current user's company.
    """
    # Ensure the customer_to matches the company the user is trying to manage
    if customer_data.customer_to != current_company.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer must belong to the specified company."
        )

    # Optional: Check for duplicate GSTIN for this company (if GSTIN is unique per company)
    if customer_data.customer_gstin:
        existing_customer_query = select(Customers).where(
            Customers.customer_gstin == customer_data.customer_gstin,
            Customers.customer_to == current_company.company_id
        )
        existing_customer_result = await db.execute(existing_customer_query)
        if existing_customer_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this GSTIN already exists for this company."
            )

    new_customer_dict = customer_data.dict() # Use dict for Pydantic v2
    new_customer = Customers(**new_customer_dict)
    db.add(new_customer)
    try:
        await db.commit()
        await db.refresh(new_customer)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {e}"
        )
    return new_customer

async def get_customer_by_id(customer_id: str, db: AsyncSession, current_company: Companies) -> Customers | None:
    """
    Service function to get a single customer by ID, ensuring it belongs to the current company.
    """
    result = await db.execute(
        select(Customers).where(
            Customers.customer_id == customer_id,
            Customers.customer_to == current_company.company_id
        )
    )
    return result.scalar_one_or_none()


async def modify_customer_details(
    customer_id: str, # Changed to str for UUID
    updated_details: UpdateCustomer,
    db: AsyncSession,
    current_company: Companies # Pass the validated company
) -> Customers:
    """
    Service function to modify customer details, ensuring it belongs to the current company.
    """
    customer = await get_customer_by_id(customer_id, db, current_company)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found or does not belong to your company."
        )

    update_data = updated_details.dict(exclude_unset=True) # Use dict for Pydantic v2

    for key, value in update_data.items():
        setattr(customer, key, value)

    try:
        await db.commit()
        await db.refresh(customer)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update customer: {e}"
        )
    return customer

async def remove_customer(
    customer_id: str, # Changed to str for UUID
    db: AsyncSession,
    current_company: Companies # Pass the validated company
) -> bool:
    """
    Service function to remove a customer, ensuring it belongs to the current company.
    """
    customer = await get_customer_by_id(customer_id, db, current_company)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found or does not belong to your company."
        )

    await db.delete(customer)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete customer: {e}"
        )
    return True