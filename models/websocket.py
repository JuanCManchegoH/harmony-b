from pydantic import BaseModel

class WebsocketResponse(BaseModel):
    event: str
    data: dict or list
    userName: str
    company: str