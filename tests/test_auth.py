import pytest
from httpx import AsyncClient

CREDENTIALS = {"username": "test_user", "password": "secret-password"}


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    """Клієнт, у якого вже є зареєстрований користувач і cookie з токеном."""
    await client.post("/api/auth/register", json=CREDENTIALS)
    return client


async def test_register_creates_user_and_sets_cookie(client: AsyncClient) -> None:
    response = await client.post("/api/auth/register", json=CREDENTIALS)

    assert response.status_code == 201
    assert response.json()["username"] == "test_user"
    assert "password_hash" not in response.json()
    assert "access_token" in response.cookies


async def test_register_duplicate_username_returns_409(
    auth_client: AsyncClient,
) -> None:
    response = await auth_client.post("/api/auth/register", json=CREDENTIALS)

    assert response.status_code == 409


async def test_me_returns_current_user(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["username"] == "test_user"


async def test_login_with_wrong_password_returns_401(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/auth/login", json={**CREDENTIALS, "password": "wrong-password"}
    )

    assert response.status_code == 401


async def test_login_sets_cookie(auth_client: AsyncClient) -> None:
    auth_client.cookies.clear()

    response = await auth_client.post("/api/auth/login", json=CREDENTIALS)

    assert response.status_code == 200
    assert "access_token" in response.cookies


async def test_logout_removes_cookie(auth_client: AsyncClient) -> None:
    await auth_client.post("/api/auth/logout")

    response = await auth_client.get("/api/auth/me")

    assert response.status_code == 401
