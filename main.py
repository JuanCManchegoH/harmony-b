"""Main module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.error_handler import ErrorHandler
from routers.companies import companies
from routers.users import users
from routers.w_fields import wfields
from routers.c_fields import cfields
from routers.positions import positions
from routers.conventions import conventions
from routers.sequences import sequences
from routers.tags import tags
from routers.customers import customers
from routers.workers import workers
from routers.stalls import stalls
from routers.shifts import shifts
from routers.logs import logs
from routers.websocket import ws

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.title = "Harmony API"
app.version = "0.0.17"

app.add_middleware(ErrorHandler)

@app.get(path="/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Harmony API!"}

app.include_router(companies)
app.include_router(users)
app.include_router(wfields)
app.include_router(cfields)
app.include_router(positions)
app.include_router(conventions)
app.include_router(sequences)
app.include_router(tags)
app.include_router(customers)
app.include_router(workers)
app.include_router(stalls)
app.include_router(shifts)
app.include_router(logs)
app.include_router(ws)
