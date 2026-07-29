import os
from pathlib import Path

UPLOAD_DIR = Path(__file__).parent / "uploads"


def get_config() -> dict[str, str]:
    return {
        "DB_PATH": os.environ.get("DB_PATH", str(Path(__file__).parent / "dev.db")),
        # dev/test fallback only — production MUST set JWT_SECRET via environment
        "JWT_SECRET": os.environ.get("JWT_SECRET", "dev-secret-hollywood-closet"),
        "JWT_EXPIRY": os.environ.get("JWT_EXPIRY", "86400"),
    }
