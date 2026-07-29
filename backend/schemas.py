from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    privacy_accepted: bool

    @field_validator("privacy_accepted")
    @classmethod
    def must_be_accepted(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Privacy policy must be accepted")
        return v


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


class ClothingItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: str
    image_path: str
    note: str | None = None

    model_config = {"from_attributes": True}


class OutfitCreate(BaseModel):
    name: str
    item_ids: list[int]


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    items: list[ClothingItemResponse] = []

    model_config = {"from_attributes": True}


class OutfitUpdate(BaseModel):
    name: str | None = None
    item_ids: list[int] | None = None
