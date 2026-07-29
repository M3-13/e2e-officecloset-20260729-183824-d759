from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str


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
    name: str = Field(min_length=1, max_length=100)
    clothing_item_ids: list[int] = Field(min_length=2)


class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    items: list[ClothingItemResponse] = []

    model_config = {"from_attributes": True}


class OutfitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    clothing_item_ids: list[int] | None = Field(default=None, min_length=2)
