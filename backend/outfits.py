import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from auth import get_current_user
from database import get_db
from models import ClothingItem, Outfit, OutfitItem, User
from schemas import ClothingItemResponse, OutfitCreate, OutfitResponse, OutfitUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


def _validate_and_fetch_items(
    db: Session, clothing_item_ids: list[int], user_id: int
) -> list[ClothingItem]:
    if len(set(clothing_item_ids)) != len(clothing_item_ids):
        raise HTTPException(status_code=400, detail="Duplicate clothing item IDs")

    items = db.query(ClothingItem).filter(ClothingItem.id.in_(clothing_item_ids)).all()

    if len(items) != len(clothing_item_ids):
        raise HTTPException(status_code=404, detail="One or more clothing items not found")

    for item in items:
        if item.user_id != user_id:
            raise HTTPException(status_code=404, detail="One or more clothing items not found")

    categories = [item.category for item in items]
    if len(set(categories)) != len(categories):
        raise HTTPException(status_code=400, detail="only one item per category allowed")

    return items


def _build_outfit_response(outfit: Outfit) -> OutfitResponse:
    return OutfitResponse(
        id=outfit.id,
        user_id=outfit.user_id,
        name=outfit.name,
        items=[ClothingItemResponse.model_validate(oi.clothing_item) for oi in outfit.items],
    )


def _load_outfit_with_items(db: Session, outfit_id: int) -> Outfit | None:
    return (
        db.query(Outfit)
        .options(joinedload(Outfit.items).joinedload(OutfitItem.clothing_item))
        .filter(Outfit.id == outfit_id)
        .first()
    )


@router.post("/", response_model=OutfitResponse, status_code=201)
def create_outfit(
    body: OutfitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OutfitResponse:
    items = _validate_and_fetch_items(db, body.clothing_item_ids, current_user.id)

    outfit = Outfit(name=body.name, user_id=current_user.id)
    db.add(outfit)
    db.flush()

    for item in items:
        db.add(OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id))

    db.commit()

    outfit = _load_outfit_with_items(db, outfit.id)
    assert outfit is not None
    logger.info("Outfit created id=%d user_id=%d", outfit.id, current_user.id)
    return _build_outfit_response(outfit)


@router.get("/", response_model=list[OutfitResponse])
def list_outfits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OutfitResponse]:
    outfits = (
        db.query(Outfit)
        .options(joinedload(Outfit.items).joinedload(OutfitItem.clothing_item))
        .filter(Outfit.user_id == current_user.id)
        .order_by(Outfit.created_at.desc())
        .all()
    )
    logger.info("Listed outfits count=%d user_id=%d", len(outfits), current_user.id)
    return [_build_outfit_response(o) for o in outfits]


@router.get("/{outfit_id}", response_model=OutfitResponse)
def get_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OutfitResponse:
    outfit = _load_outfit_with_items(db, outfit_id)
    if outfit is None or outfit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Outfit not found")
    logger.info("Got outfit id=%d user_id=%d", outfit.id, current_user.id)
    return _build_outfit_response(outfit)


@router.put("/{outfit_id}", response_model=OutfitResponse)
def update_outfit(
    outfit_id: int,
    body: OutfitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OutfitResponse:
    outfit = (
        db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user.id).first()
    )
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")

    if body.name is not None:
        outfit.name = body.name

    if body.clothing_item_ids is not None:
        items = _validate_and_fetch_items(db, body.clothing_item_ids, current_user.id)
        db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit.id).delete()
        for item in items:
            db.add(OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id))

    db.commit()

    outfit = _load_outfit_with_items(db, outfit.id)
    assert outfit is not None
    logger.info("Updated outfit id=%d user_id=%d", outfit.id, current_user.id)
    return _build_outfit_response(outfit)


@router.delete("/{outfit_id}", status_code=204)
def delete_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    outfit = (
        db.query(Outfit).filter(Outfit.id == outfit_id, Outfit.user_id == current_user.id).first()
    )
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")

    db.delete(outfit)
    db.commit()
    logger.info("Deleted outfit id=%d user_id=%d", outfit.id, current_user.id)
