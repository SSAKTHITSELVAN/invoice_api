# app/services/companies.py
from app.models.companies import Companies
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from fastapi import HTTPException, status
from app.schemas.companies import CreateCompany, UpdateCompany, CompanyOut
from app.services.users import get_current_active_user # Import the dependency for authentication
from app.models.users import Users # Import Users model for type hinting
from typing import List

async def add_company(company: CreateCompany, db: AsyncSession, current_user: Users) -> Companies:
    """Service function to add a new company, associated with the current user."""
    # Ensure the company being created is owned by the current authenticated user
    if company.company_owner != str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create companies for your own user ID."
        )

    # Check if a company with the same GSTIN already exists (if provided)
    if company.company_gstin:
        existing_company_query = select(Companies).where(Companies.company_gstin == company.company_gstin)
        existing_company_result = await db.execute(existing_company_query)
        if existing_company_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this GSTIN already exists."
            )

    new_company_data = company.dict() # Use dict for Pydantic v2
    new_company = Companies(**new_company_data)
    db.add(new_company)
    try:
        await db.commit()
        await db.refresh(new_company)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create company: {e}"
        )
    return new_company

async def delete_company(company_id: str, db: AsyncSession, current_user: Users) -> bool:
    """Service function to delete a company by ID, ensuring user ownership."""
    result = await db.execute(
        select(Companies).where(
            Companies.company_id == company_id,
            Companies.company_owner == str(current_user.user_id) # Ensure ownership
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified company not found or you don't have permission to delete it.")

    await db.delete(company)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete company: {e}"
        )
    return True

async def list_companies(db: AsyncSession, current_user: Users) -> List[Companies]:
    """Service function to list all companies owned by the current user."""
    result = await db.execute(
        select(Companies).where(Companies.company_owner == str(current_user.user_id))
    )
    companies = result.scalars().all()
    return companies

async def get_company_by_id(company_id: str, db: AsyncSession, current_user: Users) -> Companies | None:
    """Service function to get a single company by ID, ensuring user ownership."""
    result = await db.execute(
        select(Companies).where(
            Companies.company_id == company_id,
            Companies.company_owner == str(current_user.user_id)
        )
    )
    return result.scalar_one_or_none()


async def modify_company_details(company_id: str, updated_details: UpdateCompany, db: AsyncSession, current_user: Users) -> Companies:
    """Service function to update company details, ensuring user ownership."""
    result = await db.execute(
        select(Companies).where(
            Companies.company_id == company_id,
            Companies.company_owner == str(current_user.user_id) # Ensure ownership
        )
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified company not found or you don't have permission to modify it.")

    update_data = updated_details.dict(exclude_unset=True) # Use dict for Pydantic v2

    for key, value in update_data.items():
        setattr(company, key, value)

    try:
        await db.commit()
        await db.refresh(company)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update company: {e}"
        )
    return company