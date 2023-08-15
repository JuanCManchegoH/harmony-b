# routers/websocket.py
from fastapi import APIRouter, HTTPException, WebSocket, status
from models.websocket import WebsocketResponse
from services.users import UsersServices
from db.client import db_client
from utils.auth import decodeAccessToken
from services.websocket import manager

ws = APIRouter(prefix='/ws', tags=['Websocket'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]

@ws.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.headers.get("authorization")
    if token:
        token = token.split(" ")[1]
        token_data = decodeAccessToken(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    user = UsersServices(harmony).getByEmail(token_data["email"])
    await manager.connect(websocket, user["company"])
    try:
        while manager.hasActiveConnections():
            data = await websocket.receive_json()
            message = WebsocketResponse(**data)
            await manager.broadcast(message)
    except Exception as e:
        print(e)
        manager.disconnect(websocket)