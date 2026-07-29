from fastapi import APIRouter, HTTPException

from schemas import OutfitCreate, OutfitResponse, OutfitUpdate

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


@router.post("/", response_model=OutfitResponse, status_code=201)
def create_outfit(body: OutfitCreate) -> OutfitResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/", response_model=list[OutfitResponse])
def list_outfits() -> list[OutfitResponse]:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{outfit_id}", response_model=OutfitResponse)
def get_outfit(outfit_id: int) -> OutfitResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{outfit_id}", response_model=OutfitResponse)
def update_outfit(outfit_id: int, body: OutfitUpdate) -> OutfitResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{outfit_id}", status_code=204)
def delete_outfit(outfit_id: int) -> None:
    raise HTTPException(status_code=501, detail="Not implemented")
