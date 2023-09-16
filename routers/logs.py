""" Log routers module. """

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from schemas.log import log_entity, log_entity_list
from services.users import UsersServices
from services.companies import CompaniesServices
from services.logs import LogsServices
from models.log import CreateLog
from utils.auth import decode_access_token
from utils.roles import required_roles

logs = APIRouter(prefix='/logs', tags=['Logs'], responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
users_services = UsersServices(database)
def logs_services(company_db):
    """Logs services."""
    return LogsServices(company_db)

# Create log
@logs.post(
    path="",
    summary="Create log",
    description="This endpoint creates a log in the database and returns the log object.",
    status_code=201)
async def create_log(log: CreateLog, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Create log."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["super_admin"])
    # Create log
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = logs_services(company_db).create_log(log)
    result = log_entity(result)
    # Response
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# Find logs by month and year
@logs.get(
    path="/{month}/{year}",
    summary="Find logs by month and year",
    description=
    "This endpoint finds logs by month and year in the database and returns a list of log objects.",
    status_code=200)
async def find_logs_by_month_and_year(
    month: str,
    year: str,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Find logs by month and year."""
    # Validations
    token = decode_access_token(token)
    # Find logs by month and year
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = logs_services(company_db).find_logs_by_month_and_year(user["company"], month, year)
    result = log_entity_list(result)
    # Response
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Delete log
@logs.delete(
    path="/{log_id}",
    summary="Delete log",
    description="This endpoint deletes a log in the database and returns the deleted log object.",
    status_code=200)
async def delete_log(log_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete log."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["super_admin"])
    # Delete log
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = logs_services(company_db).delete_log(user["company"], log_id)
    result = log_entity(result)
    # Response
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
