# app/services/products.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.products import Products
from sqlalchemy import select, delete, update
from fastapi import HTTPException, status
from app.schemas.products import CreateProduct, UpdateProduct, ProductOut
from app.models.companies import Companies # Import Companies model
from typing import List

# Assuming get_current_company is defined in app.services.customers or a common location
# If not, you might need to import it from app.services.customers or define it here.
# For consistency, let's assume it's imported for now.
from app.services.customers import get_current_company # Reusing get_current_company dependency

async def show_products(db: AsyncSession, current_company: Companies) -> List[Products]:
    """
    Service function to list all products belonging to a specific company,
    which is owned by the current user.
    """
    result = await db.execute(
        select(Products).where(Products.company_id == current_company.company_id)
    )
    products = result.scalars().all()
    return products

async def create_products(
    product_data: CreateProduct,
    db: AsyncSession,
    current_company: Companies
) -> Products:
    """
    Service function to create a new product, ensuring it's for the current user's company.
    """
    # Ensure the company_id in the request body matches the company the user is managing
    if product_data.company_id != current_company.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product must belong to the specified company."
        )

    # Optional: Check for duplicate product name or HSN/SAC code within this company if unique
    # This example assumes uniqueness is handled at the database level or not enforced.

    new_product_dict = product_data.dict() # Use dict for Pydantic v2
    new_product = Products(**new_product_dict)
    db.add(new_product)
    try:
        await db.commit()
        await db.refresh(new_product)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {e}"
        )
    return new_product

async def get_product_by_id(product_id: str, db: AsyncSession, current_company: Companies) -> Products | None:
    """
    Service function to get a single product by ID, ensuring it belongs to the current company.
    """
    result = await db.execute(
        select(Products).where(
            Products.product_id == product_id,
            Products.company_id == current_company.company_id
        )
    )
    return result.scalar_one_or_none()

async def modify_product_details(
    product_id: str, # Changed to str for UUID
    updated_details: UpdateProduct,
    db: AsyncSession,
    current_company: Companies
) -> Products:
    """
    Service function to modify product details, ensuring it belongs to the current company.
    """
    product = await get_product_by_id(product_id, db, current_company)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or does not belong to your company.")

    update_data = updated_details.dict(exclude_unset=True) # Use dict for Pydantic v2

    for key, value in update_data.items():
        setattr(product, key, value)

    try:
        await db.commit()
        await db.refresh(product)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {e}"
        )
    return product

async def remove_products(
    product_id: str, # Changed to str for UUID
    db: AsyncSession,
    current_company: Companies
) -> bool:
    """
    Service function to remove a product, ensuring it belongs to the current company.
    """
    product = await get_product_by_id(product_id, db, current_company)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or does not belong to your company.")

    await db.delete(product)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {e}"
        )
    return True