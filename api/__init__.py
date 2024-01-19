from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Server, Config
import asyncio

from api.routers.box import router as box_router
from api.routers.character import router as character_router
from api.routers.db import router as db_router
from api.routers.documents import router as document_router
from api.routers.event import router as event_router
from api.routers.game import router as game_router
from api.routers.help import router as help_router
from api.routers.history import router as history_router
from api.routers.objective import router as objective_router
from api.routers.quizz import router as quizz_router
from api.routers.status import router as status_router
from api.routers.users import router as user_router
from api.routers.exports import router as exports_router
from api.routers.stream import router as stream_router

from api.database import close_database_connections


app = FastAPI()
# app_stream = FastAPI()

origins = [
    'http://127.0.0.1:5173',
    'http://localhost:5173',
    'http://localhost',
    'https://app2.detectivebox.fr',
    'https://detectivebox-2-app-nihbf.ondigitalocean.app',
    'https://dev-detectivebox-2-b4csu.ondigitalocean.app'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(status_router)
app.include_router(db_router)
app.include_router(document_router)
app.include_router(box_router)
app.include_router(quizz_router)
app.include_router(help_router)
app.include_router(objective_router)
app.include_router(history_router)
app.include_router(character_router)
app.include_router(event_router)
app.include_router(game_router)
app.include_router(exports_router)

# app_stream.include_router(stream_router)

@app.on_event("shutdown")
async def shutdown_event():
    close_database_connections()