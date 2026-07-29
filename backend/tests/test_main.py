from fastapi.testclient import TestClient

from main import app


def test_health_endpoint_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_auth_register_returns_501() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "secret123"},
        )
        assert response.status_code == 501


def test_auth_login_returns_501() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "secret123"},
        )
        assert response.status_code == 501


def test_auth_me_returns_501() -> None:
    with TestClient(app) as client:
        response = client.get("/api/auth/me")
        assert response.status_code == 501


def test_auth_delete_account_returns_501() -> None:
    with TestClient(app) as client:
        response = client.delete("/api/auth/account")
        assert response.status_code == 501


def test_wardrobe_list_returns_501() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wardrobe/")
        assert response.status_code == 501


def test_wardrobe_get_item_returns_501() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wardrobe/1")
        assert response.status_code == 501


def test_outfits_list_returns_501() -> None:
    with TestClient(app) as client:
        response = client.get("/api/outfits/")
        assert response.status_code == 501


def test_lifespan_creates_tables() -> None:
    from sqlalchemy import inspect

    from database import get_engine

    engine = get_engine()

    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    assert "users" in table_names
    assert "clothing_items" in table_names
    assert "outfits" in table_names
    assert "outfit_items" in table_names
