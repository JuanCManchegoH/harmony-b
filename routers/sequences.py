from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Sequence
from utils.auth import decodeAccessToken
from utils.roles import validateRoles
from utils.errorsResponses import errors
from services.users import UsersServices
from services.sequences import SequencesServices
from services.websocket import manager
from models.websocket import WebsocketResponse

sequences = APIRouter(prefix="/sequences", tags=["Sequences"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a sequence
@sequences.post(path="/", summary="Add a sequence", description="Add a sequence to a company", status_code=status.HTTP_201_CREATED)
async def addSequence(sequence: Sequence, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).addSequence(user["company"], sequence)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a sequence
@sequences.put(path="/{sequenceId}", summary="Update a sequence", description="Update a sequence from a company", status_code=status.HTTP_200_OK)
async def updateSequence(sequenceId: str, sequence: Sequence, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).updateSequence(user["company"], sequenceId, sequence)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a sequence
@sequences.delete(path="/{sequenceId}", summary="Delete a sequence", description="Delete a sequence from a company", status_code=status.HTTP_200_OK)
async def deleteSequence(sequenceId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).deleteSequence(user["company"], sequenceId)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
