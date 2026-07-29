from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import get_config
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    config = get_config()
    secret = config["JWT_SECRET"]
    token = credentials.credentials
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as err:
        raise HTTPException(status_code=401, detail="Invalid token") from err

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


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
