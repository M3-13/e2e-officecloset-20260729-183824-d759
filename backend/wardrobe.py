from fastapi import APIRouter, HTTPException, Query, UploadFile

from schemas import ClothingItemCreate, ClothingItemResponse

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])


@router.post("/", response_model=ClothingItemResponse, status_code=201)
def create_item(
    name: str,
    category: str,
    image: UploadFile,
    note: str | None = None,
) -> ClothingItemResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/", response_model=list[ClothingItemResponse])
def list_items(category: str | None = Query(default=None)) -> list[ClothingItemResponse]:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{item_id}", response_model=ClothingItemResponse)
def get_item(item_id: int) -> ClothingItemResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{item_id}", response_model=ClothingItemResponse)
def update_item(item_id: int, body: ClothingItemCreate) -> ClothingItemResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    raise HTTPException(status_code=501, detail="Not implemented")
