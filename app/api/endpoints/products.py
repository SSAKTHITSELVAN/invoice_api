# app/api/routers/products.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.products import CreateProduct, UpdateProduct, ProductOut, SingleProductResponse, ListProductResponse
from app.schemas.common import APIResponse # Import APIResponse
from app.services.products import show_products, create_products, modify_product_details, remove_products, get_product_by_id
from app.services.users import get_current_active_user # For user authentication
from app.services.customers import get_current_company # Reusing current_company dependency
from app.models.users import Users
from app.models.companies import Companies # Import Companies model

# Define the router with a nested prefix
router = APIRouter(prefix="/companies/{company_id}/products", tags=["Products"])


@router.get("/", response_model=ListProductResponse)
async def get_products_endpoint(
    company_id: str, # Path parameter for company_id
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user), # Authenticate user
    current_company: Companies = Depends(get_current_company) # Authenticate and get company
):
    """
    List all products for a specific company owned by the authenticated user.
    """
    products = await show_products(db, current_company)
    product_out_list = [
        ProductOut(
            product_id=str(p.product_id),
            company_id=str(p.company_id),
            product_name=p.product_name,
            product_description=p.product_description,
            product_hsn_sac_code=p.product_hsn_sac_code,
            product_unit_of_measure=p.product_unit_of_measure,
            product_unit_price=p.product_unit_price,
            product_default_cgst_rate=p.product_default_cgst_rate,
            product_default_sgst_rate=p.product_default_sgst_rate,
            product_default_igst_rate=p.product_default_igst_rate,
            created_at=p.created_at
        ) for p in products
    ]
    return ListProductResponse(
        status_code=status.HTTP_200_OK,
        message="Products retrieved successfully",
        data=product_out_list
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SingleProductResponse)
async def add_product_endpoint(
    company_id: str, # Path parameter for company_id
    product_data: CreateProduct, # Renamed for clarity
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Add a new product to a specific company owned by the authenticated user.
    """
    # Ensure the company_id in the request body matches the company_id from the path
    if product_data.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="company_id in request body must match company_id in path."
        )

    new_product = await create_products(product_data, db, current_company)
    return SingleProductResponse(
        status_code=status.HTTP_201_CREATED,
        message="Product added successfully",
        data=ProductOut(
            product_id=str(new_product.product_id),
            company_id=str(new_product.company_id),
            product_name=new_product.product_name,
            product_description=new_product.product_description,
            product_hsn_sac_code=new_product.product_hsn_sac_code,
            product_unit_of_measure=new_product.product_unit_of_measure,
            product_unit_price=new_product.product_unit_price,
            product_default_cgst_rate=new_product.product_default_cgst_rate,
            product_default_sgst_rate=new_product.product_default_sgst_rate,
            product_default_igst_rate=new_product.product_default_igst_rate,
            created_at=new_product.created_at
        )
    )

@router.get("/{product_id}", response_model=SingleProductResponse)
async def get_single_product_endpoint(
    company_id: str,
    product_id: str, # Changed to str for UUID
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Retrieve a single product by ID for a specific company.
    """
    product = await get_product_by_id(product_id, db, current_company)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or does not belong to your company.")
    return SingleProductResponse(
        status_code=status.HTTP_200_OK,
        message="Product retrieved successfully",
        data=ProductOut(
            product_id=str(product.product_id),
            company_id=str(product.company_id),
            product_name=product.product_name,
            product_description=product.product_description,
            product_hsn_sac_code=product.product_hsn_sac_code,
            product_unit_of_measure=product.product_unit_of_measure,
            product_unit_price=product.product_unit_price,
            product_default_cgst_rate=product.product_default_cgst_rate,
            product_default_sgst_rate=product.product_default_sgst_rate,
            product_default_igst_rate=product.product_default_igst_rate,
            created_at=product.created_at
        )
    )

@router.put("/{product_id}", response_model=SingleProductResponse)
async def updated_product_details_endpoint(
    company_id: str,
    product_id: str, # Changed to str for UUID
    updated_details: UpdateProduct,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Update details of an existing product for a specific company.
    """
    product = await modify_product_details(product_id, updated_details, db, current_company)
    return SingleProductResponse(
        status_code=status.HTTP_200_OK,
        message="Product updated successfully",
        data=ProductOut(
            product_id=str(product.product_id),
            company_id=str(product.company_id),
            product_name=product.product_name,
            product_description=product.product_description,
            product_hsn_sac_code=product.product_hsn_sac_code,
            product_unit_of_measure=product.product_unit_of_measure,
            product_unit_price=product.product_unit_price,
            product_default_cgst_rate=product.product_default_cgst_rate,
            product_default_sgst_rate=product.product_default_sgst_rate,
            product_default_igst_rate=product.product_default_igst_rate,
            created_at=product.created_at
        )
    )

@router.delete("/{product_id}", status_code=status.HTTP_200_OK, response_model=APIResponse[None])
async def delete_product_endpoint(
    company_id: str,
    product_id: str, # Changed to str for UUID
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_active_user),
    current_company: Companies = Depends(get_current_company)
):
    """
    Delete a product for a specific company.
    """
    await remove_products(product_id, db, current_company)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Product successfully deleted",
        data=None
    )