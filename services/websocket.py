"""Websocket manager to handle active connections and broadcast messages"""

from typing import List
from fastapi import WebSocket
from models.websocket import WebsocketResponse

class WebSocketManager:
    """Websocket manager"""
    def __init__(self):
        self.active_connections: List = []

    async def connect(self, websocket: WebSocket, company: str):
        """
        Connect a websocket.
        Args:
            websocket (WebSocket): Websocket.
            company (str): Company.
        """
        await websocket.accept()
        connection = {"websocket": websocket, "company": company}
        self.active_connections.append(connection)

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a websocket.
        Args:
            websocket (WebSocket): Websocket.
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, data: WebsocketResponse):
        """
        Broadcast a message to all active connections.
        Args:
            data (WebsocketResponse): Websocket response.
        """
        for connection in self.active_connections:
            if connection["company"] == data.company:
                await connection["websocket"].send_json(
                    dict(
                        event=data.event,
                        data=data.data,
                        userName=data.userName,
                        company=data.company))

    def has_active_connections(self) -> bool:
        """Check if there are active connections."""
        return bool(self.active_connections)

manager = WebSocketManager()
