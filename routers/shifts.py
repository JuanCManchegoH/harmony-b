"""Shifts router module."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from schemas.stall import stall_entity
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
async def create_shifts(data: CreateShifts , token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Create shifts."""
    print("Here")
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["admin", "create_shifts", "handle_shifts"])
    # Encode shifts
    shifts_to_create = jsonable_encoder(data.shifts)
    # Create shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = shifts_services(company_db).create_shifts(user["company"], shifts_to_create, user)
    result = [shift_entity(shift) for shift in result]
    message = (
        f"El usuario {user['userName']} ha creado los turnos y/o descansos en el puesto "
        f"{shifts_to_create[0]['stallName']}, "
        f"Persona: {shifts_to_create[0]['workerName']}, "
        f"Cliente: {shifts_to_create[0]['customerName']}, "
    )
    # Log
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "action": "create_shifts",
        "type": "Turnos, descansos o eventos",
        "message": message,
        })
    return JSONResponse(status_code=201, content=result)

@shifts.post(
    path='/getByMonthsAndYears',
    summary='Get shifts',
    description='Get shifts',
    status_code=200)
async def get_shifts(
    data: GetShifts,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Get shifts."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["admin", "read_shifts", "handle_shifts"])
    # Get shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = shifts_services(company_db).get_shifts_by_month_and_year(
        user["company"],
        data.months,
        data.years,
        data.types)
    result = [shift_entity(shift) for shift in result]
    return JSONResponse(status_code=200, content=result)

@shifts.put(path='', summary='Update shifts', description='Update shifts', status_code=200)
async def update_shifts(data: UpdateShifts, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update shifts."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["admin", "handle_shifts"])
    # Encode shifts
    shifts_to_update = jsonable_encoder(data.shifts)
    # Update shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = shifts_services(company_db).update_shifts(user["company"], shifts_to_update, user)
    result = [shift_entity(shift) for shift in result]
    # Log
    message = (
        f"El usuario {user['userName']} ha actualizado los turnos y/o descansos en el puesto "
        f"{result[0]['stallName']}, "
        f"Persona: {result[0]['workerName']}, "
        f"Cliente: {result[0]['customerName']}, "
    )
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "action": "update_shifts",
        "type": "Turnos, descansos o eventos",
        "message": message,
        })
    return JSONResponse(status_code=200, content=result)

@shifts.post(
    path='/delete/{stall_id}',
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
    allowed_roles(token["roles"], ["admin", "handle_shifts", "handle_shifts"])
    # Delete shifts
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = shifts_services(company_db).delete_shifts(user["company"], stall_id, data.shifts)
    result = [shift_entity(shift) for shift in result]
    stall = stalls_services(company_db).get_stall(stall_id)
    stall = stall_entity(stall)
    # Log
    message = (
        f"El usuario {user['userName']} ha eliminado los turnos y/o descansos en el puesto "
        f"{stall['name']}, "
        f"Cliente: {stall['customerName']}, "
    )
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "action": "delete_shifts",
        "type": "Turnos, descansos o eventos",
        "message": message,
        })
    return JSONResponse(status_code=200, content=result)

# UpdateModel (use carefully)
# @shifts.put(
#     path='/updateModel',
#     summary='Update shifts model',
#     description='Update shifts model',
#     status_code=200)
# async def update_shifts_model(token: str = Depends(oauth2_scheme)) -> JSONResponse:
#     """Update shifts model."""
#     print("update_shifts_model")
#     # Validations
#     token = decode_access_token(token)
#     allowed_roles(token["roles"], ["super_admin"])
#     # Update shifts model
#     user = users_services.get_by_email(token["email"])
#     company = companies_services.get_company(user["company"])
#     company_db = db_client[company["db"]]
#     _ = shifts_services(company_db).update_model()
#     return JSONResponse(status_code=200, content={
    # "message": "Shifts model updated successfully."})
