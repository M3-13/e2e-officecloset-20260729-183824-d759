from datetime import UTC, datetime, timedelta
from pathlib import Path

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import get_config
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()
UPLOAD_DIR = Path(__file__).parent / "uploads"


def _hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise HTTPException(status_code=422, detail="Password must be at most 72 bytes")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def _get_jwt_secret() -> str:
    secret = get_config()["JWT_SECRET"]
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET is not configured")
    return secret


def _get_jwt_expiry() -> int:
    return int(get_config()["JWT_EXPIRY"])


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=_get_jwt_expiry())
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, _get_jwt_secret(), algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, _get_jwt_secret(), algorithms=["HS256"])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token") from None
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        password_hash=_hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == body.email).first()
    if user is None or not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.delete("/account", status_code=204)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    image_paths: list[Path] = []
    for item in current_user.clothing_items:
        img_path = UPLOAD_DIR / Path(item.image_path).name
        if img_path.exists():
            image_paths.append(img_path)
    db.delete(current_user)
    db.commit()
    for img_path in image_paths:
        img_path.unlink()
