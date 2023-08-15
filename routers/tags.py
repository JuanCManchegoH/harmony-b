from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Tag
from utils.auth import decodeAccessToken, validateRoles
from services.users import UsersServices
from services.tags import TagsServices
from services.websocket import manager
from models.websocket import WebsocketResponse

tags = APIRouter(prefix="/tags", tags=["Tags"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a tag
@tags.post(path="/", summary="Add a tag", description="Add a tag to a company", status_code=status.HTTP_201_CREATED)
async def addTag(tag: Tag, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_tag"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).addTag(user["company"], tag)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error adding tag.")

# update a tag
@tags.put(path="/{tagId}", summary="Update a tag", description="Update a tag from a company", status_code=status.HTTP_200_OK)
async def updateTag(tagId: str, tag: Tag, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_tag"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).updateTag(user["company"], tagId, tag)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating tag.")

# delete a tag
@tags.delete(path="/{tagId}", summary="Delete a tag", description="Delete a tag from a company", status_code=status.HTTP_200_OK)
async def deleteTag(tagId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_tag"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).deleteTag(user["company"], tagId)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting tag.")