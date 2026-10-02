from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.memory.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)