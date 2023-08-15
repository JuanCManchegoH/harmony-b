from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Field
from utils.auth import decodeAccessToken, validateRoles
from services.users import UsersServices
from services.cFields import CFieldsServices
from services.websocket import manager
from models.websocket import WebsocketResponse

cfields = APIRouter(prefix="/cfields", tags=["CFields"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a customer field
@cfields.post(path="/", summary="Add a customer field", description="Add a customer field to a company", status_code=status.HTTP_201_CREATED)
async def addCField(field: Field, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_cfield"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = CFieldsServices(db).addCField(user["company"], field)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error adding customer field.")

# update a customer field
@cfields.put(path="/{fieldId}", summary="Update a customer field", description="Update a customer field from a company", status_code=status.HTTP_200_OK)
async def updateCField(fieldId: str, field: Field, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_cfield"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = CFieldsServices(db).updateCField(user["company"], fieldId, field)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating customer field.")

# delete a customer field
@cfields.delete(path="/{fieldId}", summary="Delete a customer field", description="Delete a customer field from a company", status_code=status.HTTP_200_OK)
async def deleteCField(fieldId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_cfield"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = CFieldsServices(db).deleteCField(user["company"], fieldId)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting customer field.")