import os
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from jose import jwt

from database import get_engine
from main import app
from models import Base, Category, ClothingItem, User

TEST_SECRET = "test-secret"


def _create_test_db():
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine


def _make_token(user_id: int, secret: str = TEST_SECRET, expiry: int = 86400) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {"sub": str(user_id), "exp": now + timedelta(seconds=expiry)},
        secret,
        algorithm="HS256",
    )


def _auth_headers(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token(user_id)}"}


def test_health_endpoint_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_wardrobe_list_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wardrobe/")
        assert response.status_code == 401


def test_wardrobe_get_item_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.get("/api/wardrobe/1")
        assert response.status_code == 401


class TestAuth:
    @classmethod
    def setup_class(cls):
        os.environ["JWT_SECRET"] = TEST_SECRET
        cls.engine = _create_test_db()

    @classmethod
    def teardown_class(cls):
        os.environ.pop("JWT_SECRET", None)

    def _register(self, client: TestClient, email: str, password: str = "password123"):
        return client.post(
            "/api/auth/register",
            json={"email": email, "password": password},
        )

    def _login(self, client: TestClient, email: str, password: str = "password123"):
        return client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )

    def test_register_success(self):
        with TestClient(app) as client:
            resp = self._register(client, "newuser@test.com")
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate(self):
        email = "dup@test.com"
        with TestClient(app) as client:
            r1 = self._register(client, email)
            assert r1.status_code == 201
            r2 = self._register(client, email)
        assert r2.status_code == 409

    def test_register_short_password(self):
        with TestClient(app) as client:
            resp = client.post(
                "/api/auth/register",
                json={"email": "short@test.com", "password": "1234567"},
            )
        assert resp.status_code == 422

    def test_register_invalid_email(self):
        with TestClient(app) as client:
            resp = client.post(
                "/api/auth/register",
                json={"email": "not-an-email", "password": "password123"},
            )
        assert resp.status_code == 422

    def test_login_success(self):
        email = "login1@test.com"
        with TestClient(app) as client:
            self._register(client, email)
            resp = self._login(client, email)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        email = "login2@test.com"
        with TestClient(app) as client:
            self._register(client, email)
            resp = self._login(client, email, "wrongpassword")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self):
        with TestClient(app) as client:
            resp = self._login(client, "nobody@test.com")
        assert resp.status_code == 401

    def test_get_me_success(self):
        email = "me1@test.com"
        with TestClient(app) as client:
            reg_resp = self._register(client, email)
            token = reg_resp.json()["access_token"]
            resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == email
        assert "id" in data

    def test_get_me_no_auth(self):
        with TestClient(app) as client:
            resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self):
        with TestClient(app) as client:
            resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not.valid.token"})
        assert resp.status_code == 401

    def test_get_me_expired_token(self):
        with TestClient(app) as client:
            token = _make_token(9999, TEST_SECRET, expiry=-1)
            resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_delete_account(self):
        email = "delme@test.com"
        with TestClient(app) as client:
            reg_resp = self._register(client, email)
            token = reg_resp.json()["access_token"]
            resp = client.delete("/api/auth/account", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 204

    def test_delete_account_no_auth(self):
        with TestClient(app) as client:
            resp = client.delete("/api/auth/account")
        assert resp.status_code == 401

    def test_delete_account_invalid_token(self):
        with TestClient(app) as client:
            resp = client.delete(
                "/api/auth/account", headers={"Authorization": "Bearer bad.token.here"}
            )
        assert resp.status_code == 401

    def test_cannot_use_deleted_account(self):
        email = "gone@test.com"
        with TestClient(app) as client:
            reg_resp = self._register(client, email)
            token = reg_resp.json()["access_token"]
            client.delete("/api/auth/account", headers={"Authorization": f"Bearer {token}"})
            resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_full_auth_flow(self):
        with TestClient(app) as client:
            reg_resp = client.post(
                "/api/auth/register",
                json={"email": "flow@test.com", "password": "flowpass12"},
            )
            assert reg_resp.status_code == 201
            token = reg_resp.json()["access_token"]

            login_resp = client.post(
                "/api/auth/login",
                json={"email": "flow@test.com", "password": "flowpass12"},
            )
            assert login_resp.status_code == 200

            me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me_resp.status_code == 200
            assert me_resp.json()["email"] == "flow@test.com"

            del_resp = client.delete(
                "/api/auth/account", headers={"Authorization": f"Bearer {token}"}
            )
            assert del_resp.status_code == 204

            me_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me_after.status_code == 401


def test_lifespan_creates_tables() -> None:
    from sqlalchemy import inspect

    engine = get_engine()

    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    assert "users" in table_names
    assert "clothing_items" in table_names
    assert "outfits" in table_names
    assert "outfit_items" in table_names


class TestOutfitsCRUD:
    @classmethod
    def setup_class(cls):
        os.environ["JWT_SECRET"] = TEST_SECRET
        cls.engine = _create_test_db()

    @classmethod
    def teardown_class(cls):
        os.environ.pop("JWT_SECRET", None)

    def _create_user(self, email: str = "test@example.com") -> User:
        from database import _get_sessionlocal

        session = _get_sessionlocal()()
        user = User(email=email, password_hash="hashed")
        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()
        return user

    def _create_item(
        self,
        user_id: int,
        name: str = "Test Shirt",
        category: Category = Category.OBERTOPS,
        image_path: str = "test.jpg",
    ) -> ClothingItem:
        from database import _get_sessionlocal

        session = _get_sessionlocal()()
        item = ClothingItem(
            user_id=user_id,
            name=name,
            category=category,
            image_path=image_path,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        session.close()
        return item

    def test_create_outfit_success(self):
        user = self._create_user("create1@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "Casual Look", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Casual Look"
        assert data["user_id"] == user.id
        assert len(data["items"]) == 2

    def test_create_outfit_requires_min_2_items(self):
        user = self._create_user("create2@test.com")

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "Lonely Look", "clothing_item_ids": [999]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 422

    def test_create_outfit_name_too_long(self):
        user = self._create_user("create3@test.com")

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "A" * 101, "clothing_item_ids": [1, 2]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 422

    def test_create_outfit_name_rejects_xss(self):
        user = self._create_user("xss1@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={
                    "name": "<script>alert(1)</script>",
                    "clothing_item_ids": [item1.id, item2.id],
                },
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 422

    def test_create_outfit_name_rejects_angle_brackets(self):
        user = self._create_user("xss2@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "bad>name", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 422

    def test_create_outfit_name_rejects_control_chars(self):
        user = self._create_user("xss3@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "bad\x00name", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 422

    def test_update_outfit_name_rejects_xss(self):
        user = self._create_user("xss4@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "Safe Name", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.put(
                f"/api/outfits/{outfit_id}",
                json={"name": "<img src=x onerror=alert(1)>"},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 422

    def test_create_outfit_items_must_belong_to_user(self):
        user1 = self._create_user("owner@test.com")
        user2 = self._create_user("other@test.com")
        item = self._create_item(user2.id, "Stolen Item", Category.SCHUHE)
        my_item = self._create_item(user1.id, "My Shirt", Category.OBERTOPS)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "Stolen Outfit", "clothing_item_ids": [item.id, my_item.id]},
                headers=_auth_headers(user1.id),
            )

        assert resp.status_code == 404

    def test_create_outfit_nonexistent_item(self):
        user = self._create_user("create4@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "Missing Item", "clothing_item_ids": [item1.id, 99999]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 404

    def test_create_outfit_duplicate_category(self):
        user = self._create_user("create5@test.com")
        item1 = self._create_item(user.id, "Red Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Blue Shirt", Category.OBERTOPS)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "Two Tops", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 400
        assert "only one item per category" in resp.json()["detail"]

    def test_create_outfit_duplicate_ids(self):
        user = self._create_user("create6@test.com")
        item = self._create_item(user.id, "Shirt", Category.OBERTOPS)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "Double", "clothing_item_ids": [item.id, item.id]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 400

    def test_create_outfit_requires_auth(self):
        user = self._create_user("create7@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            resp = client.post(
                "/api/outfits/",
                json={"name": "No Auth", "clothing_item_ids": [item1.id, item2.id]},
            )

        assert resp.status_code == 401

    def test_list_outfits_empty(self):
        user = self._create_user("list1@test.com")

        with TestClient(app) as client:
            resp = client.get("/api/outfits/", headers=_auth_headers(user.id))

        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_outfits_returns_user_outfits(self):
        user = self._create_user("list2@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)
        item3 = self._create_item(user.id, "Sneakers", Category.SCHUHE)

        with TestClient(app) as client:
            resp1 = client.post(
                "/api/outfits/",
                json={"name": "Outfit A", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )
            assert resp1.status_code == 201

            resp2 = client.post(
                "/api/outfits/",
                json={"name": "Outfit B", "clothing_item_ids": [item2.id, item3.id]},
                headers=_auth_headers(user.id),
            )
            assert resp2.status_code == 201

            resp = client.get("/api/outfits/", headers=_auth_headers(user.id))

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["name"] == "Outfit B"
        assert data[1]["name"] == "Outfit A"

    def test_list_outfits_isolated_per_user(self):
        user1 = self._create_user("list3@test.com")
        user2 = self._create_user("list4@test.com")
        item_a = self._create_item(user1.id, "Shirt A", Category.OBERTOPS)
        item_b = self._create_item(user1.id, "Jeans A", Category.HOSEN)
        item_c = self._create_item(user2.id, "Shirt B", Category.OBERTOPS)
        item_d = self._create_item(user2.id, "Jeans B", Category.HOSEN)

        with TestClient(app) as client:
            client.post(
                "/api/outfits/",
                json={"name": "User1 Outfit", "clothing_item_ids": [item_a.id, item_b.id]},
                headers=_auth_headers(user1.id),
            )
            client.post(
                "/api/outfits/",
                json={"name": "User2 Outfit", "clothing_item_ids": [item_c.id, item_d.id]},
                headers=_auth_headers(user2.id),
            )

            resp = client.get("/api/outfits/", headers=_auth_headers(user1.id))

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "User1 Outfit"

    def test_get_outfit_success(self):
        user = self._create_user("get1@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "My Outfit", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.get(f"/api/outfits/{outfit_id}", headers=_auth_headers(user.id))

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == outfit_id
        assert data["name"] == "My Outfit"
        assert len(data["items"]) == 2

    def test_get_outfit_not_found(self):
        user = self._create_user("get2@test.com")

        with TestClient(app) as client:
            resp = client.get("/api/outfits/99999", headers=_auth_headers(user.id))

        assert resp.status_code == 404

    def test_get_outfit_wrong_user(self):
        user1 = self._create_user("get3@test.com")
        user2 = self._create_user("get4@test.com")
        item1 = self._create_item(user1.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user1.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "Mine", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user1.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.get(f"/api/outfits/{outfit_id}", headers=_auth_headers(user2.id))

        assert resp.status_code == 404

    def test_update_outfit_name_only(self):
        user = self._create_user("update1@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "Old Name", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.put(
                f"/api/outfits/{outfit_id}",
                json={"name": "New Name"},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert len(data["items"]) == 2

    def test_update_outfit_items_only(self):
        user = self._create_user("update2@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)
        item3 = self._create_item(user.id, "Sneakers", Category.SCHUHE)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "Outfit", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.put(
                f"/api/outfits/{outfit_id}",
                json={"clothing_item_ids": [item2.id, item3.id]},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Outfit"
        assert len(data["items"]) == 2
        item_ids = {i["id"] for i in data["items"]}
        assert item_ids == {item2.id, item3.id}

    def test_update_outfit_not_found(self):
        user = self._create_user("update3@test.com")

        with TestClient(app) as client:
            resp = client.put(
                "/api/outfits/99999",
                json={"name": "Ghost"},
                headers=_auth_headers(user.id),
            )

        assert resp.status_code == 404

    def test_update_outfit_wrong_user(self):
        user1 = self._create_user("update4@test.com")
        user2 = self._create_user("update5@test.com")
        item1 = self._create_item(user1.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user1.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "Mine", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user1.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.put(
                f"/api/outfits/{outfit_id}",
                json={"name": "Stolen"},
                headers=_auth_headers(user2.id),
            )

        assert resp.status_code == 404

    def test_delete_outfit_success(self):
        user = self._create_user("del1@test.com")
        item1 = self._create_item(user.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "To Delete", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.delete(f"/api/outfits/{outfit_id}", headers=_auth_headers(user.id))

        assert resp.status_code == 204

        with TestClient(app) as client:
            get_resp = client.get(f"/api/outfits/{outfit_id}", headers=_auth_headers(user.id))

        assert get_resp.status_code == 404

    def test_delete_outfit_not_found(self):
        user = self._create_user("del2@test.com")

        with TestClient(app) as client:
            resp = client.delete("/api/outfits/99999", headers=_auth_headers(user.id))

        assert resp.status_code == 404

    def test_delete_outfit_wrong_user(self):
        user1 = self._create_user("del3@test.com")
        user2 = self._create_user("del4@test.com")
        item1 = self._create_item(user1.id, "Shirt", Category.OBERTOPS)
        item2 = self._create_item(user1.id, "Jeans", Category.HOSEN)

        with TestClient(app) as client:
            create_resp = client.post(
                "/api/outfits/",
                json={"name": "Mine", "clothing_item_ids": [item1.id, item2.id]},
                headers=_auth_headers(user1.id),
            )
            outfit_id = create_resp.json()["id"]

            resp = client.delete(f"/api/outfits/{outfit_id}", headers=_auth_headers(user2.id))

        assert resp.status_code == 404

    def test_outfits_require_auth(self):
        with TestClient(app) as client:
            assert client.get("/api/outfits/").status_code == 401
            assert client.get("/api/outfits/1").status_code == 401
            assert client.put("/api/outfits/1", json={"name": "X"}).status_code == 401
            assert client.delete("/api/outfits/1").status_code == 401
