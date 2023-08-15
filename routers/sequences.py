from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Sequence
from utils.auth import decodeAccessToken, validateRoles
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_sequence"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).addSequence(user["company"], sequence)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error adding sequence.")

# update a sequence
@sequences.put(path="/{sequenceId}", summary="Update a sequence", description="Update a sequence from a company", status_code=status.HTTP_200_OK)
async def updateSequence(sequenceId: str, sequence: Sequence, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_sequence"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).updateSequence(user["company"], sequenceId, sequence)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating sequence.")

# delete a sequence
@sequences.delete(path="/{sequenceId}", summary="Delete a sequence", description="Delete a sequence from a company", status_code=status.HTTP_200_OK)
async def deleteSequence(sequenceId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_sequence"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).deleteSequence(user["company"], sequenceId)
    if result:
        message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting sequence.")
