import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import tickets
from app.db.database import create_tables

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(tickets.router)


@app.get("/")
def root() -> dict[str, str]:
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    return {"status": "ok"}
