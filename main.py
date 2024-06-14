from ipaddress import ip_address
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException

from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as redis


from src.database.db import get_db
from src.routes import contacts as contacts_routes
from src.routes import auth as auth_routes
from src.routes import users as users_routes
from src.config.config import config


app = FastAPI()

banned_ips = [
    ip_address("192.168.1.1"),
    ip_address("192.168.1.2"),
    ip_address("127.0.0.1"),
]

origin = ["*"]
# origin = ["http://localhost:5500"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(".")

# app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(auth_routes.router, prefix="/api")
app.include_router(users_routes.router, prefix="/api")
app.include_router(contacts_routes.router, prefix="/api")


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        db=0,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def index():
    return {"message": "Contact aplication goit-python-web-hw13-p1"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {
            "message": "Welcome to FastAPI! HealthChecker goit-python-web-hw13-p1 - OK"
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
