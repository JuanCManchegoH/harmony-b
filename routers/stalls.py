from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from models.shift import DeleteShifts
from services.users import UsersServices
from services.companies import CompaniesServices
from services.stalls import StallsServices
from services.websocket import manager
from models.stall import GetStalls, Stall, StallWorker, UpdateStall
from models.websocket import WebsocketResponse
from schemas.stall import StallEntity, StallsAndShifts
from utils.auth import decodeAccessToken
from utils.roles import allowed_roles

stalls = APIRouter(prefix='/stalls', tags=['Stalls'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create a stall
@stalls.post(path="", summary="Create a stall", description="This endpoint creates a stall in the database and returns the stall object.", status_code=201)
async def createStall(stall: Stall, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Create stall
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = StallsServices(companyDb).createStall(stall, user)
    result = StallEntity(result)
    # Websocket
    message = WebsocketResponse(event="stall_created", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# find stalls
@stalls.post(path="/getByCustomer", summary="Find all stalls", description="This endpoint returns all stalls", status_code=200)
async def finsCustomerStalls(data: GetStalls, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["read_stalls", "admin"])
    # Find all stalls
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    if data.customerId:
        result = StallsServices(companyDb).finsCustomerStalls(user["company"], data.customerId, data.months, data.years)
        result = StallsAndShifts(result["stalls"], result["shifts"])
    else:
        result = StallsServices(companyDb).findStalls(user["company"], data.months, data.years)
        result = StallsAndShifts(result["stalls"], result["shifts"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# update a stall
@stalls.put(path="/{id}", summary="Update a stall", description="This endpoint updates a stall in the database and returns the stall object.", status_code=200)
async def updateStall(id: str, data: UpdateStall, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Update stall
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = StallsServices(companyDb).updateStall(id, data, user)
    result = StallEntity(result)
    # Websocket
    message = WebsocketResponse(event="stall_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return result

# delete a stall
@stalls.post(path="/{id}", summary="Delete a stall", description="This endpoint deletes a stall in the database and returns the stall object.", status_code=200)
async def deleteStall(id: str, data: DeleteShifts, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Delete stall
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = StallsServices(companyDb).deleteStall(user["company"], id, data.shifts)
    result = StallEntity(result)
    # Websocket
    message = WebsocketResponse(event="stall_deleted", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return result

# Stall worker
@stalls.post(path="/addWorker/{id}", summary="Add a worker to a stall", description="This endpoint adds a worker to a stall in the database and returns the stall object.", status_code=200)
async def addStallWorker(id: str, worker: StallWorker, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Create stall worker
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = StallsServices(companyDb).addStallWorker(id, worker, user)
    result = StallEntity(result)
    # Websocket
    message = WebsocketResponse(event="stall_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return result

@stalls.post(path="/removeWorker/{id}/{workerId}", summary="Remove a worker from a stall", description="This endpoint removes a worker from a stall in the database and returns the stall object.", status_code=200)
async def removeWorker(id: str, workerId: str, data: DeleteShifts, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Delete stall worker
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = StallsServices(companyDb).removeWorker(user["company"], id, workerId, data.shifts)
    result = StallEntity(result)
    # Websocket
    message = WebsocketResponse(event="stall_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return result
    