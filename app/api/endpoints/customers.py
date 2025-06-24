from app.api.router.customers import router
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.customers import CreateCustomer, UpdateCustomer
from fastapi import status, Depends
from app.database import get_db
from app.services.customers import list_all_customers, create_new_customer, modify_customer_details, remove_customer
from app.models.users import Users
from app.services.users import get_current_user


@router.get("/customers")
async def show_customers(db: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_user)):
    customers = await list_all_customers(db)
    return customers

@router.post("/customers", status_code=status.HTTP_201_CREATED)
async def add_new_customer(customer: CreateCustomer, db: AsyncSession = Depends(get_db)):
    new_customer = await create_new_customer(customer, db)
    return new_customer

@router.put("/customer/{customer_id}")
async def update_customer(customer_id: int, updated_customer: UpdateCustomer, db: AsyncSession = Depends(get_db)):
    customer = await modify_customer_details(customer_id, updated_customer, db)
    return customer

@router.delete("/customer/{customer_id}")
async def delete_customer(customer_id: int ,  db: AsyncSession = Depends(get_db)):
    message = await remove_customer(customer_id, db)
    return message