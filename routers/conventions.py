from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Convention
from utils.auth import decodeAccessToken, validateRoles
from services.users import UsersServices
from services.conventions import ConventionsServices
from services.websocket import manager
from models.websocket import WebsocketResponse

conventions = APIRouter(prefix="/conventions", tags=["Conventions"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a convention
@conventions.post(path="/", summary="Add a convention", description="Add a convention to a company", status_code=status.HTTP_201_CREATED)
async def addConvention(convention: Convention, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_convention"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).addConvention(user["company"], convention)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error adding convention.")

# update a convention
@conventions.put(path="/{conventionId}", summary="Update a convention", description="Update a convention from a company", status_code=status.HTTP_200_OK)
async def updateConvention(conventionId: str, convention: Convention, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_convention"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).updateConvention(user["company"], conventionId, convention)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating convention.")

# delete a convention
@conventions.delete(path="/{conventionId}", summary="Delete a convention", description="Delete a convention from a company", status_code=status.HTTP_200_OK)
async def deleteConvention(conventionId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_convention"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).deleteConvention(user["company"], conventionId)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting convention.")