from sqlalchemy.ext.asyncio import AsyncSession
from app.models.products import Products
from sqlalchemy import select
from fastapi import HTTPException, status

async def show_products(db: AsyncSession):
    result = await db.execute(select(Products))
    products = result.scalars().all()
    return products

async def create_products(product, db: AsyncSession):
    try:
        new_product = Products(**product.dict())
        db.add(new_product)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Once again correct the inputted details")
    await db.refresh(new_product)
    return new_product

async def modify_product_details(product_id, updated_details, db: AsyncSession):
    result = await db.execute(select(Products).where(Products.product_id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such product")
    
    updated_detail = updated_details.dict(exclude_unset=True)
    try:
        for key, value in updated_detail.items():
            setattr(product, key, value)
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Once again correct the inputted details --> {e}")
    return product

async def remove_products(product_id, db: AsyncSession):
    result = await db.execute(select(Products).where(Products.product_id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such product")
    await db.delete(product)
    await db.commit()
    return {"message": "Product successfully deleted..."}