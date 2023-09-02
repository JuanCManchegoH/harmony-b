from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from services.users import UsersServices
from services.companies import CompaniesServices
from services.shifts import ShiftsServices
from services.websocket import manager
from models.shift import CreateAndUpdateShifts
from models.websocket import WebsocketResponse
from schemas.shift import ShiftsEntity
from utils.auth import decodeAccessToken
from utils.roles import allowed_roles
from typing import List

shifts = APIRouter(prefix='/shifts', tags=['Shifts'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create and update shifts
@shifts.put(path="/", summary="Create and update shifts", description="This endpoint creates and updates shifts in the database and returns the shifts object.", status_code=201)
async def createAndUpdateShifts(shifts: CreateAndUpdateShifts, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_shifts", "admin"])
    # Create and update shifts
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    if len(shifts.create) > 0:
        createResult = ShiftsServices(companyDb).createShifts(user["company"], shifts.create, user)
    else:
        createResult = []
    if len(shifts.update) > 0:
        updateResult = ShiftsServices(companyDb).updateShifts(user["company"], shifts.update, user)
    else:
        updateResult = []
    result = {
        "created": ShiftsEntity(createResult),
        "updated": ShiftsEntity(updateResult)
    }
    # Websocket
    # message = WebsocketResponse(event="shifts_created_and_updated", data=result, userName=user["userName"], company=user["company"])
    # await manager.broadcast(message)
    # Return
    return result

# delete shifts
@shifts.delete(path="/", summary="Delete shifts", description="This endpoint deletes shifts in the database and returns the shifts object.", status_code=200)
async def deleteShifts(shifts: List[str], token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_shifts", "admin"])
    # Delete shifts
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = ShiftsServices(companyDb).deleteShifts(user["company"], shifts[0]["stall"], shifts)
    result = ShiftsEntity(result)
    # Websocket
    message = WebsocketResponse(event="shifts_deleted", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return result