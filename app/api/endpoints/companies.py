# app/api/routers/companies.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.companies import CreateCompany, UpdateCompany, CompanyOut, SingleCompanyResponse, ListCompanyResponse
from app.schemas.common import APIResponse # Import APIResponse
from app.services.companies import add_company, delete_company, list_companies, modify_company_details, get_company_by_id
from app.services.users import get_current_active_user # Import authentication dependency
from app.models.users import Users # Import Users model for type hinting

# Define the router here. Do not import from app.api.router.companies
router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SingleCompanyResponse)
async def create_company_endpoint(
    company: CreateCompany,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user) # Add authentication
):
    """
    Create a new company.
    The company will be associated with the authenticated user.
    """
    new_company = await add_company(company, db, current_user)
    return SingleCompanyResponse(
        status_code=status.HTTP_201_CREATED,
        message="Company created successfully",
        data=CompanyOut(
            company_id=str(new_company.company_id), # Ensure UUID is string
            company_owner=str(new_company.company_owner), # Ensure UUID is string
            company_name=new_company.company_name,
            company_address=new_company.company_address,
            company_city=new_company.company_city,
            company_state=new_company.company_state,
            company_gstin=new_company.company_gstin,
            company_msme=new_company.company_msme,
            company_email=new_company.company_email,
            company_bank_account_no=new_company.company_bank_account_no,
            company_bank_name=new_company.company_bank_name,
            company_account_holder=new_company.company_account_holder,
            company_branch=new_company.company_branch,
            company_ifsc_code=new_company.company_ifsc_code,
            created_at=new_company.created_at,
            # customers=[] # Uncomment if you enable customers field in CompanyOut
        )
    )

@router.delete("/{company_id}", status_code=status.HTTP_200_OK, response_model=APIResponse[None])
async def remove_company_endpoint(
    company_id: str, # Changed to str for UUID
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user) # Add authentication
):
    """
    Delete a company by its ID.
    Only the owner can delete their company.
    """
    await delete_company(company_id, db, current_user)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Company successfully deleted",
        data=None # No data returned for delete success
    )

@router.get("/", response_model=ListCompanyResponse)
async def get_companies_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user) # Add authentication
):
    """
    Get a list of all companies owned by the authenticated user.
    """
    companies = await list_companies(db, current_user)
    company_out_list = [
        CompanyOut(
            company_id=str(c.company_id),
            company_owner=str(c.company_owner),
            company_name=c.company_name,
            company_address=c.company_address,
            company_city=c.company_city,
            company_state=c.company_state,
            company_gstin=c.company_gstin,
            company_msme=c.company_msme,
            company_email=c.company_email,
            company_bank_account_no=c.company_bank_account_no,
            company_bank_name=c.company_bank_name,
            company_account_holder=c.company_account_holder,
            company_branch=c.company_branch,
            company_ifsc_code=c.company_ifsc_code,
            created_at=c.created_at,
            # customers=[]
        ) for c in companies
    ]
    return ListCompanyResponse(
        status_code=status.HTTP_200_OK,
        message="Companies retrieved successfully",
        data=company_out_list
    )

@router.get("/{company_id}", response_model=SingleCompanyResponse)
async def get_single_company_endpoint(
    company_id: str, # Changed to str for UUID
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user) # Add authentication
):
    """
    Get a single company by its ID.
    Only the owner can view their company.
    """
    company = await get_company_by_id(company_id, db, current_user)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found or you don't have permission to view it.")
    return SingleCompanyResponse(
        status_code=status.HTTP_200_OK,
        message="Company retrieved successfully",
        data=CompanyOut(
            company_id=str(company.company_id),
            company_owner=str(company.company_owner),
            company_name=company.company_name,
            company_address=company.company_address,
            company_city=company.company_city,
            company_state=company.company_state,
            company_gstin=company.company_gstin,
            company_msme=company.company_msme,
            company_email=company.company_email,
            company_bank_account_no=company.company_bank_account_no,
            company_bank_name=company.company_bank_name,
            company_account_holder=company.company_account_holder,
            company_branch=company.company_branch,
            company_ifsc_code=company.company_ifsc_code,
            created_at=company.created_at,
            # customers=[]
        )
    )

@router.put("/{company_id}", response_model=SingleCompanyResponse)
async def update_company_details_endpoint(
    company_id: str, # Changed to str for UUID
    company_update: UpdateCompany, # Renamed for clarity
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user) # Add authentication
):
    """
    Update details of an existing company.
    Only the owner can update their company.
    """
    updated_company = await modify_company_details(company_id, company_update, db, current_user)
    return SingleCompanyResponse(
        status_code=status.HTTP_200_OK,
        message="Company updated successfully",
        data=CompanyOut(
            company_id=str(updated_company.company_id),
            company_owner=str(updated_company.company_owner),
            company_name=updated_company.company_name,
            company_address=updated_company.company_address,
            company_city=updated_company.company_city,
            company_state=updated_company.company_state,
            company_gstin=updated_company.company_gstin,
            company_msme=updated_company.company_msme,
            company_email=updated_company.company_email,
            company_bank_account_no=updated_company.company_bank_account_no,
            company_bank_name=updated_company.company_bank_name,
            company_account_holder=updated_company.company_account_holder,
            company_branch=updated_company.company_branch,
            company_ifsc_code=updated_company.company_ifsc_code,
            created_at=updated_company.created_at,
            # customers=[]
        )
    )