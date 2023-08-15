from pydantic import BaseModel

class WebsocketResponse(BaseModel):
    event: str
    data: dict
    userName: str
    company: str