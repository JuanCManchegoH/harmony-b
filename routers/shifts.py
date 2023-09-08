from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from schemas.stall import StallEntity
from services.users import UsersServices
from services.companies import CompaniesServices
from services.shifts import ShiftsServices
from services.stalls import StallsServices
from services.websocket import manager
from services.logs import LogsServices
from models.shift import CreateAndUpdateShifts, DeleteShifts
from models.websocket import WebsocketResponse
from schemas.shift import ShiftsEntity
from utils.auth import decodeAccessToken
from utils.roles import allowed_roles
from typing import List

shifts = APIRouter(prefix='/shifts', tags=['Shifts'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create and update shifts
@shifts.put(path="", summary="Create and update shifts", description="This endpoint creates and updates shifts in the database and returns the shifts object.", status_code=201)
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
    if shifts.appliedSequence:
        # data is equal to dict witth shifts.appliedSequence["sequence"], shifts.appliedSequence["index"], shifts.appliedSequence["jump"] without shifts.appliedSequence["stall"]
        appliedSequence = dict(shifts.appliedSequence)
        steps = [dict(step) for step in appliedSequence["sequence"]]
        print("Here")
        data = {
            "sequence": steps,
            "index": appliedSequence["index"],
            "jump": appliedSequence["jump"]
        }
        print(steps)
        stall = StallsServices(companyDb).updateStallWorker(appliedSequence["stall"], appliedSequence["worker"], data, user)  
    else:
        stall = {}
    result = {
        "created": ShiftsEntity(createResult),
        "updated": ShiftsEntity(updateResult),
        "stall": StallEntity(stall) if shifts.appliedSequence else None
    }
    # Websocket
    # message = WebsocketResponse(event="shifts_created_and_updated", data=result, userName=user["userName"], company=user["company"])
    # await manager.broadcast(message)
    # Log
    if len(shifts.create) > 0:
        create = dict(shifts.create[0])
        stall = StallsServices(companyDb).findStall(create["stall"])
    if len(shifts.update) > 0:
        update = dict(shifts.update[0])
        stall = StallsServices(companyDb).findStall(update["stall"])
    stall = dict(stall)
    _ = LogsServices(companyDb).createLog({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Turnos",
        "message": f"El usuario {user['userName']} ha creado y/o actualizado turnos en el puesto {stall['name']}. Cliente: {stall['customerName']}"
    })
    # Return
    return result

# delete shifts
@shifts.post(path="/delete/{stallId}", summary="Delete shifts", description="This endpoint deletes shifts in the database and returns the shifts object.", status_code=200)
async def deleteShifts(stallId: str, data:DeleteShifts, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_shifts", "admin"])
    # Delete shifts
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    print(data.shifts)
    result = ShiftsServices(companyDb).deleteShifts(user["company"], stallId, data.shifts)
    result = ShiftsEntity(result)
    # Websocket
    # message = WebsocketResponse(event="shifts_deleted", data=result, userName=user["userName"], company=user["company"])
    # await manager.broadcast(message)\
    # Log
    stall = StallsServices(companyDb).findStall(stallId)
    stall = dict(stall)
    _ = LogsServices(companyDb).createLog({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Turnos",
        "message": f"El usuario {user['userName']} ha eliminado turnos en el puesto {stall['name']}. Cliente: {stall['customerName']}"
    })
    # Return
    return result