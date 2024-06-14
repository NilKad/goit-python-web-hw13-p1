from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(None, max_length=20)
    email: str = EmailStr
    birthday: Optional[str] = None
    # birthday: Optional[str] = Field(None, max_length=10)
    # birthday: str = Field(None, max_length=10)
    # birthday: Optional[datetime] = Field(None, format="%Y-%m-%d")
    addition: Optional[str] = Field(None, max_length=250)

    @field_validator("birthday")
    def validate_birthday(cls, v):
        if v and not v == "":
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. It should be YYYY-MM-DD.")
        return v


class ContactResponse(ContactSchema):
    id: int = 1
    first_name: str
    last_name: str
    phone: str
    email: str
    birthday: str | None
    addition: str | None
    user: UserResponse | None

    class Config:
        from_attributes: True
