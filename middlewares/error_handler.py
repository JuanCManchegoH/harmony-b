from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class ErrorHandler(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        
    async def dispatch(self, request: Request, call_next) -> Response :
        try:
            return await call_next(request)
        except Exception as e:
            print(e)
            return Response("Internal server error", status_code=500)