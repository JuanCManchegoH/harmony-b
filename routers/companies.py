from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from models.company import Company, UpdateCompany
from utils.auth import decodeAccessToken
from utils.roles import validateRoles
from services.companies import CompaniesServices
from utils.errorsResponses import errors

companies = APIRouter(prefix='/companies', tags=['Companies'], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a company
@companies.post(path="/", summary="Create a company", description="This endpoint creates a company in the database and returns the company object.", status_code=201)
async def createCompany(company: Company, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["super_admin"], []):
        raise errors["Unauthorized"]
    result = CompaniesServices(db).createCompany(company)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# Find one company
@companies.get(path="/{id}", summary="Find a company", description="This endpoint finds a company in the database and returns the company object.", status_code=200)
async def findCompany(id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["super_admin"], []):
        raise errors["Unauthorized"]
    result = CompaniesServices(db).findCompany(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Find all companies
@companies.get(path="/", summary="Find all companies", description="This endpoint finds all companies in the database and returns a list of company objects.", status_code=200)
async def findAllCompanies(token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["super_admin"], []):
        raise errors["Unauthorized"]
    result = CompaniesServices(db).findAllCompanies()
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
# Update a company
@companies.put(path="/{id}", summary="Update a company", description="This endpoint updates a company in the database and returns the updated company object.", status_code=200)
async def updateCompany(id: str, company: UpdateCompany, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["super_admin"], []):
        raise errors["Unauthorized"]
    result = CompaniesServices(db).updateCompany(id, company)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Delete a company
@companies.delete(path="/{id}", summary="Delete a company", description="This endpoint deletes a company from the database and returns the deleted company object.", status_code=200)
async def deleteCompany(id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["super_admin"], []):
        raise errors["Unauthorized"]
    result = CompaniesServices(db).deleteCompany(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)