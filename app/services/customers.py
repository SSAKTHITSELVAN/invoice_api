from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.customers import Customers
from sqlalchemy import select

async def list_all_customers(db: AsyncSession):
    result = await db.execute(select(Customers))
    customers = result.scalars().all()
    return customers

async def create_new_customer(customer, db: AsyncSession):
    new_customer = Customers(**customer.dict())
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer

async def modify_customer_details(customer_id, updated_details, db: AsyncSession):
    result = await db.execute(select(Customers).where(Customers.customer_id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer of specific ide not found")
    
    updated_details = updated_details.dict(exclude_unset=True)
    for key, value in updated_details.items():
        setattr(customer, key, value)
    await db.commit()
    return customer

async def remove_customer(customer_id, db: AsyncSession):
    result = await db.execute(select(Customers).where(Customers.customer_id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer of specific ide not found")
    
    await db.delete(customer)
    await db.commit()
    return {'message': 'Customer successfully deleted...'}