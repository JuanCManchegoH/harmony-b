from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from services.users import UsersServices
from services.positions import PositionsServices
from services.websocket import manager
from models.company import Position
from models.websocket import WebsocketResponse
from schemas.company import CompanyEntity
from utils.auth import decodeAccessToken
from utils.roles import required_roles

positions = APIRouter(prefix="/positions", tags=["Positions"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a position
@positions.post(path="", summary="Add a position", description="Add a position to a company", status_code=status.HTTP_201_CREATED)
async def addPosition(position: Position, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Add position
    user = UsersServices(db).getByEmail(token["email"])
    result = PositionsServices(db).addPosition(user["company"], position)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a position
@positions.put(path="/{positionId}", summary="Update a position", description="Update a position from a company", status_code=status.HTTP_200_OK)
async def updatePosition(positionId: str, position: Position, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Update position
    user = UsersServices(db).getByEmail(token["email"])
    result = PositionsServices(db).updatePosition(user["company"], positionId, position)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a position
@positions.delete(path="/{positionId}", summary="Delete a position", description="Delete a position from a company", status_code=status.HTTP_200_OK)
async def deletePosition(positionId: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Delete position
    user = UsersServices(db).getByEmail(token["email"])
    result = PositionsServices(db).deletePosition(user["company"], positionId)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)