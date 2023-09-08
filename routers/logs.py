from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from schemas.log import LogEntity, LogsEntity
from services.users import UsersServices
from services.companies import CompaniesServices
from services.logs import LogsServices
from models.log import CreateLog
from utils.auth import decodeAccessToken
from utils.roles import required_roles
from typing import List

logs = APIRouter(prefix='/logs', tags=['Logs'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Create log
@logs.post(path="", summary="Create log", description="This endpoint creates a log in the database and returns the log object.", status_code=201)
async def createLog(log: CreateLog, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["super_admin"])
    # Create log
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = LogsServices(companyDb).createLog(log)
    result = LogEntity(result)
    # Response
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# Find logs by month and year
@logs.get(path="/{month}/{year}", summary="Find logs by month and year", description="This endpoint finds logs by month and year in the database and returns a list of log objects.", status_code=200)
async def findLogsByMonthAndYear(month: str, year: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    # Find logs by month and year
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = LogsServices(companyDb).findLogsByMonthAndYear(user["company"], month, year)
    result = LogsEntity(result)
    # Response
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Delete log
@logs.delete(path="/{id}", summary="Delete log", description="This endpoint deletes a log in the database and returns the deleted log object.", status_code=200)
async def deleteLog(id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["super_admin"])
    # Delete log
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = LogsServices(companyDb).deleteLog(user["company"], id)
    result = LogEntity(result)
    # Response
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)