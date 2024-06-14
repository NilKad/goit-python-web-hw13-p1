import logging
import select
from typing import Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Depends,
    Request,
    Response,
    status,
    Path,
    Query,
    Security,
)
from fastapi.responses import FileResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
    HTTPBearer,
)
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.email import send_email
from src.database.db import get_db

# from src.entity.models import Todo
from src.repositories import users as repositories_users
from src.schemas.user import RequestEmail, UserSchema, UserResponse, TokenSchema
from src.services.auth import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])

get_refresh_token = HTTPBearer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post(
    "/signup",
    response_model=Optional[UserResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=2, seconds=60))],
)
async def signup(
    body: UserSchema,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.add_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

    # print()
    # new_user = User(
    #     email=body.username, password=hash_handler.get_password_hash(body.password)
    # )

    return new_user


@router.post("/login", response_model=Optional[TokenSchema])
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await repositories_users.get_user_by_email(body.username, db)
    # user = db.query(User).filter(User.email == body.username).first()
    if user is None:
        logger.error("User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not auth_service.verify_password(body.password, user.password):
        logger.error("password incorrect")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=Optional[TokenSchema])
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    print(credentials.credentials)
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/request_email/{email}")
async def resend_request_email(
    email: str,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repositories_users.get_user_by_email(email, db)

    if user.is_verified:
        return {"message": "Your email is already confirmed"}
    if user:
        bt.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.is_verified:
        return {"message": "Your email is already confirmed"}
    if user:
        bt.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    print(user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.is_verified:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirm_email(email, db)
    print("ok confirmed")
    return {"message": "Email confirmed"}


# @router.get("/{username}")
# async def confirm_open_email(
#     username: str, response: Response, db: AsyncSession = Depends(get_db)
# ):
#     print("-----------------------------------")
#     print(f"{username} письмо было открыто")
#     return FileResponse(
#         "src/static/pixel.png",
#         media_type="image/png",
#         content_disposition_type="inline",
#     )
