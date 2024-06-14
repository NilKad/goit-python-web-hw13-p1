from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

# from src.database.db import get_db
from src.schemas.user import UserSchema
from src.models.models import User


async def get_user_by_email(email, db: AsyncSession):
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def add_user(body: UserSchema, db: AsyncSession):
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()


async def confirm_email(email: str, db: AsyncSession):
    user = await get_user_by_email(email, db)
    user.is_verified = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession):
    user = await get_user_by_email(email, db)
    print(user.username)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
