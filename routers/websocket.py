"""Websocket router module."""

from fastapi import APIRouter, HTTPException, WebSocket, status
from models.websocket import WebsocketResponse
from services.users import UsersServices
from services.websocket import manager
from db.client import db_client
from utils.auth import decode_access_token

class Error(Exception):
    """Base class for exceptions in this module."""

ws = APIRouter(prefix='/ws', tags=['Websocket'], responses={404: {"description": "Not found"}})
database = db_client["harmony"]
users_services = UsersServices(database)

@ws.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    """Websocket endpoint."""
    token = websocket.headers.get("authorization")
    if token:
        token = token.split(" ")[1]
        token_data = decode_access_token(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    user = users_services.get_by_email(token_data["email"])
    await manager.connect(websocket, user["company"])
    try:
        while manager.has_active_connections():
            data = await websocket.receive_json()
            message = WebsocketResponse(**data)
            await manager.broadcast(message)
    except Exception as exception:
        await manager.disconnect(websocket)
        raise Error(f"Error on websocket: {exception}") from exception
