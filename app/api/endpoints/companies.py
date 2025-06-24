from app.api.router.companies import router
from app.schemas.companies import CreateCompany, UpdateCompany, CompanyOut
from app.services.companies import add_company, delete_company, list_companies, modify_company_details
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from fastapi import Depends, status
from typing import List


@router.post("/companies", status_code= status.HTTP_201_CREATED)
async def create_company(company: CreateCompany, db: AsyncSession = Depends(get_db)):
    new_company = await add_company(company, db)
    print("company--> created successfully !")
    return new_company

@router.delete("/companies/{company_id}")
async def remove_company(company_id: int, db: AsyncSession = Depends(get_db)):
    message = await delete_company(company_id, db)
    return message

@router.get("/companies", response_model=List[CompanyOut])
async def get_companies(db: AsyncSession = Depends(get_db)):
    companies = await list_companies(db)
    return companies

@router.put("/companies/{company_id}")
async def update_company_details(company_id: int, company: UpdateCompany, db: AsyncSession = Depends(get_db)):
    company = await modify_company_details(company_id, company, db)
    return company