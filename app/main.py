from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_db_and_tables
from app.routes import auth, playlist, track


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Rhythmix API", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(track.router, prefix="/track", tags=["Tracks"])
app.include_router(playlist.router, prefix="/playlist", tags=["Playlists"])
