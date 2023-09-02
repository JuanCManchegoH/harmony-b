from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from models.company import Company, UpdateCompany
from schemas.company import CompanyEntity, CompanyEntityList
from utils.auth import decodeAccessToken
from utils.roles import required_roles
from services.companies import CompaniesServices

companies = APIRouter(prefix='/companies', tags=['Companies'], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a company
@companies.post(path="/", summary="Create a company", description="This endpoint creates a company in the database and returns the company object.", status_code=201)
async def createCompany(company: Company, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["super_admin"])
    # Create company
    result = CompaniesServices(db).createCompany(company)
    result = CompanyEntity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# Find one company
@companies.get(path="/{id}", summary="Find a company", description="This endpoint finds a company in the database and returns the company object.", status_code=200)
async def findCompany(id: str, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["super_admin"])
    # Find company
    result = CompaniesServices(db).findCompany(id)
    result = CompanyEntity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Find all companies
@companies.get(path="/", summary="Find all companies", description="This endpoint finds all companies in the database and returns a list of company objects.", status_code=200)
async def findAllCompanies(token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["super_admin"])
    # Find all companies
    result = CompaniesServices(db).findAllCompanies()
    result = CompanyEntityList(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
# Update a company
@companies.put(path="/{id}", summary="Update a company", description="This endpoint updates a company in the database and returns the updated company object.", status_code=200)
async def updateCompany(id: str, company: UpdateCompany, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["super_admin"])
    # Update company
    result = CompaniesServices(db).updateCompany(id, company)
    result = CompanyEntity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Delete a company
@companies.delete(path="/{id}", summary="Delete a company", description="This endpoint deletes a company from the database and returns the deleted company object.", status_code=200)
async def deleteCompany(id: str, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["super_admin"])
    # Delete company
    result = CompaniesServices(db).deleteCompany(id)
    result = CompanyEntity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)