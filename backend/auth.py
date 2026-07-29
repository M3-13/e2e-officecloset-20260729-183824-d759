import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from config import get_config
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIR = Path(__file__).parent / "uploads"


def _create_token(user_id: int) -> str:
    config = get_config()
    secret = config.get("JWT_SECRET", "")
    expiry_seconds = int(config.get("JWT_EXPIRY", "86400"))
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
    return jwt.encode(
        {"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(seconds=expiry_seconds)},
        secret,
        algorithm="HS256",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    config = get_config()
    secret = config.get("JWT_SECRET", "")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")

    try:
        payload = jwt.decode(credentials.credentials, secret, algorithms=["HS256"])
        user_id: int = int(payload["sub"])
    except (JWTError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials") from None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    body: UserCreate,
    db: Session = Depends(get_db),
) -> TokenResponse:
    existing = db.query(User).filter(User.email == body.email).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = pwd_context.hash(body.password)
    user = User(email=body.email, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = _create_token(user.id)
    logger.info("User registered id=%d", user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.query(User).filter(User.email == body.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_token(user.id)
    logger.info("User logged in id=%d", user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.delete("/account", status_code=204)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    from models import ClothingItem

    items = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id).all()
    for item in items:
        _delete_image_file(item.image_path)

    db.delete(current_user)
    db.commit()
    logger.info("Account deleted id=%d", current_user.id)


def _delete_image_file(image_path: str) -> None:
    try:
        full_path = UPLOAD_DIR / Path(image_path).name
        if full_path.exists():
            os.remove(full_path)
    except OSError:
        logger.warning("Could not delete image file: %s", image_path, exc_info=True)
