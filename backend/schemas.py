import re

from pydantic import BaseModel, EmailStr, Field, field_validator

_SAFE_NAME_RE = re.compile(r"^[^<>\x00-\x08\x0b\x0c\x0e-\x1f]*$")
_SAFE_NAME_MSG = "Name contains forbidden characters"


def _validate_name(value: str) -> str:
    if not _SAFE_NAME_RE.match(value):
        raise ValueError(_SAFE_NAME_MSG)
    return value


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClothingItemCreate(BaseModel):
    name: str
    category: str
    note: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_name(v)


class ClothingItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: str
    image_path: str
    note: str | None = None

    model_config = {"from_attributes": True}


class OutfitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    clothing_item_ids: list[int] = Field(min_length=2)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_name(v)


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    items: list[ClothingItemResponse] = []

    model_config = {"from_attributes": True}


class OutfitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    clothing_item_ids: list[int] | None = Field(default=None, min_length=2)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_name(v)
