"""Shifts router module."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
# from schemas.stall import stall_entity
from schemas.shift import shift_entity
from services.users import UsersServices
from services.companies import CompaniesServices
from services.shifts import ShiftsServices
from services.stalls import StallsServices
# from services.websocket import manager
from services.logs import LogsServices
from models.shift import GetShifts, CreateShifts, UpdateShifts, DeleteShifts
# from models.websocket import WebsocketResponse
from utils.auth import decode_access_token
from utils.roles import allowed_roles

shifts = APIRouter(prefix='/shifts', tags=['Shifts'], responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
users_services = UsersServices(database)
companies_services = CompaniesServices(database)
def stalls_services(company_db: Database):
    """Stalls services."""
    return StallsServices(company_db)
def shifts_services(company_db: Database):
    """Shifts services."""
    return ShiftsServices(company_db)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

@shifts.post(path='', summary='Create shifts', description='Create shifts', status_code=201)
async def create_shifts(data: CreateShifts, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Create shifts."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["admin", "manager"])
    # Encode shifts
    shifts_to_create = jsonable_encoder(data.shifts)
    # Create shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = shifts_services(company_db).create_shifts(user["company"], shifts_to_create, user)
    result = [shift_entity(shift) for shift in result]
    # Log
    _ = logs_services(company_db).create_log({
        "user": user["userName"],
        "company": user["company"],
        "action": "create_shifts",
        "data": shifts})
    return JSONResponse(status_code=201, content=result)

@shifts.get(path='', summary='Get shifts', description='Get shifts', status_code=200)
async def get_shifts(
    data: GetShifts,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Get shifts."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["admin", "manager", "worker"])
    # Get shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    shifts_to_get = shifts_services(company_db).get_shifts_by_month_and_year(
        user["company"],
        data.months,
        data.years,
        data.types)
    shifts_to_get = [shift_entity(shift) for shift in shifts_to_get]
    return JSONResponse(status_code=200, content=shifts)

@shifts.put(path='', summary='Update shifts', description='Update shifts', status_code=200)
async def update_shifts(data: UpdateShifts, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update shifts."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["admin", "manager"])
    # Encode shifts
    shifts_to_update = jsonable_encoder(data.shifts)
    # Update shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = shifts_services(company_db).update_shifts(user["company"], shifts_to_update, user)
    result = [shift_entity(shift) for shift in result]
    # Log
    _ = logs_services(company_db).create_log({
        "user": user["userName"],
        "company": user["company"],
        "action": "update_shifts",
        "data": shifts})
    return JSONResponse(status_code=200, content=result)

@shifts.delete(
    path='/{stall_id}',
    summary='Delete shifts',
    description='Delete shifts',
    status_code=200)
async def delete_shifts(
    stall_id: str,
    data: DeleteShifts,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete shifts."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["admin", "manager"])
    # Delete shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = shifts_services(company_db).delete_shifts(user["company"], stall_id, data.shifts)
    result = [shift_entity(shift) for shift in result]
    # Log
    _ = logs_services(company_db).create_log({
        "user": user["userName"],
        "company": user["company"],
        "action": "delete_shifts",
        "data": data.shifts})
    return JSONResponse(status_code=200, content=result)
