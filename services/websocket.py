# services/websocket.py
from fastapi import WebSocket
from models.websocket import WebsocketResponse
from typing import List

class WebSocketManager:
    def __init__(self):
        self.active_connections: List = []

    async def connect(self, websocket: WebSocket, company: str):
        await websocket.accept()
        connection = {"websocket": websocket, "company": company}
        self.active_connections.append(connection)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, data: WebsocketResponse):
        for connection in self.active_connections:
            if connection["company"] == data.company:
                await connection["websocket"].send_json(dict(event=data.event, data=data.data, userName=data.userName, company=data.company))
    
    def hasActiveConnections(self):
        return bool(self.active_connections) 
        
            
manager = WebSocketManager()  