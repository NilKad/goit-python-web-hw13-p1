from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/goit-python-web-hw13-p1"
    )
    SECRET_KEY_JWT: str = "12!@34#$56%^78&*90()"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "demo@demo.com"
    MAIL_PASSWORD: str = "demo.demo.com"
    MAIL_FROM: str = "demo@demo.com"
    MAIL_PORT: int = 567
    MAIL_SERVER: str = "mx.demo.com"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None
    CLOUDINARY_NAME: str = "dgknpebaeaaaa"
    CLOUDINARY_KEY: str = "378313744372551343423"
    CLOUDINARY_SECRET: str = "yNI8-dr_gzp7H_3LJHjIUMNMBJ"
    # CLOUDINARY_URL: str = (
    #     "cloudinary://{378313744372551}:{CLOUDINARY_SECRET}@{CLOUDINARY_NAME}"
    # )

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ["HS256", "HS512"]:
            raise ValueError(f"{v} is not a valid algorithm")
        return v

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )


config = Settings()
