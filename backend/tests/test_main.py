import os
import tempfile
import uuid

from fastapi.testclient import TestClient

os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-do-not-use-in-prod"
os.environ["JWT_EXPIRY"] = "3600"
os.environ["DB_PATH"] = str(tempfile.mktemp(suffix=".db"))

from main import app


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


def _register(client: TestClient, email: str, password: str = "secret1234") -> dict:
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "privacy_accepted": True},
    )
    return resp.json()


class TestHealth:
    def test_health_endpoint_returns_200(self) -> None:
        with TestClient(app) as client:
            response = client.get("/api/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}


class TestRegister:
    def test_register_creates_user_and_returns_token(self) -> None:
        with TestClient(app) as client:
            email = _unique_email()
            resp = client.post(
                "/api/auth/register",
                json={
                    "email": email,
                    "password": "secret1234",
                    "privacy_accepted": True,
                },
            )
            assert resp.status_code == 201
            data = resp.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    def test_register_duplicate_email_returns_409(self) -> None:
        with TestClient(app) as client:
            email = _unique_email()
            payload = {
                "email": email,
                "password": "secret1234",
                "privacy_accepted": True,
            }
            r1 = client.post("/api/auth/register", json=payload)
            assert r1.status_code == 201
            r2 = client.post("/api/auth/register", json=payload)
            assert r2.status_code == 409

    def test_register_short_password_returns_422(self) -> None:
        with TestClient(app) as client:
            resp = client.post(
                "/api/auth/register",
                json={
                    "email": _unique_email(),
                    "password": "short",
                    "privacy_accepted": True,
                },
            )
            assert resp.status_code == 422

    def test_register_invalid_email_returns_422(self) -> None:
        with TestClient(app) as client:
            resp = client.post(
                "/api/auth/register",
                json={
                    "email": "not-an-email",
                    "password": "secret1234",
                    "privacy_accepted": True,
                },
            )
            assert resp.status_code == 422

    def test_register_missing_privacy_returns_422(self) -> None:
        with TestClient(app) as client:
            resp = client.post(
                "/api/auth/register",
                json={"email": _unique_email(), "password": "secret1234"},
            )
            assert resp.status_code == 422

    def test_register_privacy_false_returns_422(self) -> None:
        with TestClient(app) as client:
            resp = client.post(
                "/api/auth/register",
                json={
                    "email": _unique_email(),
                    "password": "secret1234",
                    "privacy_accepted": False,
                },
            )
            assert resp.status_code == 422


class TestLogin:
    def test_login_with_valid_credentials_returns_token(self) -> None:
        with TestClient(app) as client:
            email = _unique_email()
            _register(client, email)
            resp = client.post(
                "/api/auth/login",
                json={"email": email, "password": "secret1234"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self) -> None:
        with TestClient(app) as client:
            email = _unique_email()
            _register(client, email)
            resp = client.post(
                "/api/auth/login",
                json={"email": email, "password": "wrongpass"},
            )
            assert resp.status_code == 401

    def test_login_nonexistent_email_returns_401(self) -> None:
        with TestClient(app) as client:
            resp = client.post(
                "/api/auth/login",
                json={"email": "nobody@example.com", "password": "secret1234"},
            )
            assert resp.status_code == 401


class TestMe:
    def test_me_returns_user_info(self) -> None:
        with TestClient(app) as client:
            email = _unique_email()
            data = _register(client, email)
            token = data["access_token"]
            resp = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            user_data = resp.json()
            assert user_data["email"] == email
            assert "id" in user_data

    def test_me_no_token_returns_401(self) -> None:
        with TestClient(app) as client:
            resp = client.get("/api/auth/me")
            assert resp.status_code == 401

    def test_me_invalid_token_returns_401(self) -> None:
        with TestClient(app) as client:
            resp = client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer invalid-token"},
            )
            assert resp.status_code == 401


class TestDeleteAccount:
    def test_delete_account_returns_204(self) -> None:
        with TestClient(app) as client:
            email = _unique_email()
            data = _register(client, email)
            token = data["access_token"]
            resp = client.delete(
                "/api/auth/account",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 204

    def test_delete_account_cleans_up_user(self) -> None:
        with TestClient(app) as client:
            email = _unique_email()
            data = _register(client, email)
            token = data["access_token"]
            client.delete(
                "/api/auth/account",
                headers={"Authorization": f"Bearer {token}"},
            )
            login_resp = client.post(
                "/api/auth/login",
                json={"email": email, "password": "secret1234"},
            )
            assert login_resp.status_code == 401

    def test_delete_account_no_token_returns_401(self) -> None:
        with TestClient(app) as client:
            resp = client.delete("/api/auth/account")
            assert resp.status_code == 401


class TestLifespan:
    def test_lifespan_creates_tables(self) -> None:
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
