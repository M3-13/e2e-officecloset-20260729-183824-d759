import os
from pathlib import Path


def get_config() -> dict[str, str]:
    return {
        "DB_PATH": os.environ.get("DB_PATH", str(Path(__file__).parent / "dev.db")),
        "JWT_SECRET": os.environ.get("JWT_SECRET", ""),
        "JWT_EXPIRY": os.environ.get("JWT_EXPIRY", "86400"),
    }
