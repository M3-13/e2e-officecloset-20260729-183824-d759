from fastapi import APIRouter, HTTPException

from schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserCreate) -> TokenResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/me", response_model=UserResponse)
def get_me() -> UserResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/account", status_code=204)
def delete_account() -> None:
    raise HTTPException(status_code=501, detail="Not implemented")
