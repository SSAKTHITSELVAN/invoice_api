from app.api.router.products import router
from app.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.products import show_products, create_products, modify_product_details, remove_products
from app.schemas.products import CreateProduct, UpdateProduct

@router.get('/products')
async def get_products(db: AsyncSession = Depends(get_db)):
    products = await show_products(db)
    return products

@router.post("/products")
async def add_product(product: CreateProduct, db: AsyncSession = Depends(get_db)):
    new_product = await create_products(product, db)
    return new_product

@router.put("/products/{product_id}")
async def updated_product_details(product_id: int, updated_details: UpdateProduct, db: AsyncSession = Depends(get_db)):
    product = await modify_product_details(product_id, updated_details, db)
    return product

@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    message = await remove_products(product_id, db)
    return message