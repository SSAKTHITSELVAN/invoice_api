from app.models.companies import Companies
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

async def add_company(company, db: AsyncSession):
    new_company = Companies(**company.dict())
    db.add(new_company)
    await db.commit()
    await db.refresh(new_company)
    return new_company

async def delete_company(comapny_id: int, db: AsyncSession):
    result = await db.execute(select(Companies).where(Companies.company_id == comapny_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified company not found ...")
    await db.delete(company)
    await db.commit()
    return {'message': 'Company successfully deleted'}

async def list_companies(db: AsyncSession):
    result = await db.execute(select(Companies))
    companies = result.scalars().all()
    return companies

async def modify_company_details(company_id: int, updated_details, db: AsyncSession):
    result = await db.execute(select(Companies).where(Companies.company_id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified company not found ...")
    updated_details = updated_details.dict(exclude_unset = True)
    for key, value in updated_details.items():
        setattr(company, key, value)
    await db.commit()
    return updated_details