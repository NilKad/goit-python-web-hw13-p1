import pickle
import cloudinary
import cloudinary.uploader

from typing import Optional
from fastapi import (
    APIRouter,
    File,
    Depends,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from src.schemas.user import UserResponse
from src.models.models import User

from src.services.auth import auth_service

from src.database.db import get_db
from src.config.config import config
from src.repositories import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_KEY,
    api_secret=config.CLOUDINARY_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=Optional[UserResponse],
    dependencies=[Depends(RateLimiter(times=2, seconds=10))],
)
async def get_current_uesr(user: User = Depends(auth_service.get_current_user)):
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=20))],
)
async def set_user_avatar(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    public_id = f"web21/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    print(f"cloudinary res: {res}")
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user
