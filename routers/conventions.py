from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Convention
from utils.auth import decodeAccessToken
from utils.roles import validateRoles
from utils.errorsResponses import errors
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
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).addConvention(user["company"], convention)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a convention
@conventions.put(path="/{conventionId}", summary="Update a convention", description="Update a convention from a company", status_code=status.HTTP_200_OK)
async def updateConvention(conventionId: str, convention: Convention, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).updateConvention(user["company"], conventionId, convention)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a convention
@conventions.delete(path="/{conventionId}", summary="Delete a convention", description="Delete a convention from a company", status_code=status.HTTP_200_OK)
async def deleteConvention(conventionId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"] 
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).deleteConvention(user["company"], conventionId)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)