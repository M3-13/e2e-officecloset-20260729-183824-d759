from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

import models  # noqa: F401  ensure models are registered on metadata before create_all
from auth import router as auth_router
from database import Base, get_engine
from outfits import router as outfits_router
from wardrobe import router as wardrobe_router

UPLOAD_DIR = Path(__file__).parent / "uploads"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"

UPLOAD_DIR.mkdir(exist_ok=True)


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Hollywood Closet", lifespan=lifespan)

app.add_middleware(CSPMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if UPLOAD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(UPLOAD_DIR)), name="static")

app.include_router(auth_router)
app.include_router(wardrobe_router)
app.include_router(outfits_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
