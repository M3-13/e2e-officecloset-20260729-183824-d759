import logging
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from auth import get_current_user
from config import UPLOAD_DIR
from database import get_db
from models import Category, ClothingItem, User
from schemas import ClothingItemResponse
from upload import save_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

_NAME_RE = re.compile(r"^[a-zA-Z0-9äöüßÄÖÜ \-_.,;:!?&()/+\#'\"]{1,100}$")
_MAX_NOTE_LENGTH = 2000


def _validate_name(name: str) -> None:
    if not _NAME_RE.match(name):
        raise HTTPException(
            status_code=400,
            detail="Name must be 1-100 characters and contain only letters, digits, spaces, and basic punctuation.",
        )


def _validate_note(note: str | None) -> str | None:
    if note is None:
        return None
    stripped = note.strip()
    if not stripped:
        return None
    if len(stripped) > _MAX_NOTE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Note must be at most {_MAX_NOTE_LENGTH} characters.",
        )
    if "<" in stripped or ">" in stripped:
        raise HTTPException(
            status_code=400,
            detail="Note must not contain HTML tags.",
        )
    return stripped


def _validate_category(category: str) -> Category:
    try:
        return Category(category)
    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}. Valid values: {[c.value for c in Category]}",
        ) from err


def _get_owned_item(item_id: int, user: User, db: Session) -> ClothingItem:
    item = db.query(ClothingItem).filter(ClothingItem.id == item_id).first()
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ClothingItemResponse, status_code=201)
def create_item(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    note: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClothingItemResponse:
    _validate_name(name)
    cat = _validate_category(category)
    validated_note = _validate_note(note)

    image_path = save_image(image)

    item = ClothingItem(
        user_id=current_user.id,
        name=name,
        category=cat,
        image_path=image_path,
        note=validated_note,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    logger.info("Item %s created", item.id)
    return ClothingItemResponse.model_validate(item)


@router.get("/", response_model=list[ClothingItemResponse])
def list_items(
    category: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ClothingItemResponse]:
    query = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id)
    if category:
        try:
            cat = Category(category)
        except ValueError as err:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category filter: {category}",
            ) from err
        query = query.filter(ClothingItem.category == cat)
    items = query.order_by(ClothingItem.created_at.desc()).all()
    return [ClothingItemResponse.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=ClothingItemResponse)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClothingItemResponse:
    item = _get_owned_item(item_id, current_user, db)
    return ClothingItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=ClothingItemResponse)
def update_item(
    item_id: int,
    name: str = Form(...),
    category: str = Form(...),
    note: str | None = Form(None),
    image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ClothingItemResponse:
    item = _get_owned_item(item_id, current_user, db)

    _validate_name(name)
    cat = _validate_category(category)
    validated_note = _validate_note(note)

    item.name = name
    item.category = cat
    item.note = validated_note

    if image and image.filename:
        old_path = item.image_path
        new_path = save_image(image)
        item.image_path = new_path
        try:
            old_file = UPLOAD_DIR / old_path
            if old_file.exists():
                old_file.unlink()
        except OSError:
            pass
        logger.info("Item %s image replaced", item.id)

    db.commit()
    db.refresh(item)

    logger.info("Item %s updated", item.id)
    return ClothingItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    item = _get_owned_item(item_id, current_user, db)

    image_path = item.image_path
    db.delete(item)
    db.commit()

    try:
        img_file = UPLOAD_DIR / image_path
        if img_file.exists():
            img_file.unlink()
    except OSError:
        pass

    logger.info("Item %s deleted", item_id)
    return None
