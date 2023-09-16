"""Companies router module."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from db.client import db_client
from models.company import Company, UpdateCompany
from schemas.company import company_entity, company_entity_list
from utils.auth import decode_access_token
from utils.roles import required_roles
from services.companies import CompaniesServices

companies = APIRouter(
    prefix='/companies', tags=['Companies'], responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)

@companies.post(
    path="",
    summary="Create a company",
    description="This endpoint creates a company in the database and returns the company object.",
    status_code=201)
async def create_company(company: Company, token: str = Depends(oauth2_scheme)):
    """Create a company."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["super_admin"])
    # encode company
    company = jsonable_encoder(company)
    # Create company
    result = companies_services.create_company(company)
    result = company_entity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@companies.get(
    path="/{company_id}",
    summary="Find a company",
    description="This endpoint finds a company in the database and returns the company object.",
    status_code=200)
async def get_company(company_id: str, token: str = Depends(oauth2_scheme)):
    """get a company."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["super_admin"])
    # Find company
    result = companies_services.get_company(company_id)
    result = company_entity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@companies.get(
    path="",
    summary="Find all companies",
    description=
    "This endpoint finds all companies in the database and returns a list of company objects.",
    status_code=200)
async def get_all_companies(token: str = Depends(oauth2_scheme)):
    """get all companies."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["super_admin"])
    # Find all companies
    result = companies_services.get_all_companies()
    result = company_entity_list(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@companies.put(
    path="/{company_id}",
    summary="Update a company",
    description=
    "This endpoint updates a company in the database and returns the updated company object.",
    status_code=200)
async def update_company(
    company_id: str,
    company: UpdateCompany,
    token: str = Depends(oauth2_scheme)):
    """Update a company."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["super_admin"])
    # encode company
    company = jsonable_encoder(company)
    # Update company
    result = companies_services.update_company(company_id, company)
    result = company_entity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Delete a company
@companies.delete(
    path="/{company_id}",
    summary="Delete a company",
    description=
    "This endpoint deletes a company from the database and returns the deleted company object.",
    status_code=200)
async def delete_company(company_id: str, token: str = Depends(oauth2_scheme)):
    """Delete a company."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["super_admin"])
    # Delete company
    result = companies_services.delete_company(company_id)
    result = company_entity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
