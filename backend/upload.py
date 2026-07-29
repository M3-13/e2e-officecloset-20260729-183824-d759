from fastapi import HTTPException, UploadFile


def save_image(file: UploadFile) -> str:
    raise HTTPException(status_code=501, detail="Not implemented")
