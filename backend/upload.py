import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from config import UPLOAD_DIR

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"image/jpeg", "image/png"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


def save_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Only JPEG and PNG are allowed.",
        )

    contents = file.file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image too large. Maximum size is 5 MB.",
        )

    file.file.seek(0)

    ext = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png"):
        ext = ".jpg"

    filename = f"{uuid.uuid4()}{ext}"

    UPLOAD_DIR.mkdir(exist_ok=True)

    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as f:
        f.write(contents)

    relative_path = f"uploads/{filename}"
    logger.info("Image saved: %s", relative_path)
    return relative_path
