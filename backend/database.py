from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_config

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def _get_config() -> dict[str, str]:
    return get_config()


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        config = _get_config()
        _engine = create_engine(
            f"sqlite:///{config['DB_PATH']}",
            connect_args={"check_same_thread": False},
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def _get_sessionlocal() -> sessionmaker:
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


class Base(DeclarativeBase):
    pass


def get_db() -> Session:
    db = _get_sessionlocal()()
    try:
        yield db
    finally:
        db.close()
