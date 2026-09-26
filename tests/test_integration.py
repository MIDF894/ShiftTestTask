import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post("/token", data={"username": "testuser", "password": "1234"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post("/token", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_me(client: AsyncClient, user_auth_headers: dict):
    response = await client.get("/users/me/", headers=user_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_rooms(client: AsyncClient, user_auth_headers: dict):
    response = await client.get("/rooms/", headers=user_auth_headers)
    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) >= 2


@pytest.mark.asyncio
async def test_create_booking_success(client: AsyncClient, user_auth_headers: dict):
    response = await client.post(
        "/rooms/1/1/booking/",
        json={"booking_date": "2026-10-01"},
        headers=user_auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["room_id"] == 1
    assert data["booking_date"] == "2026-10-01"


@pytest.mark.asyncio
async def test_create_booking_conflict_409(client: AsyncClient, user_auth_headers: dict):
    await client.post(
        "/rooms/1/1/booking/",
        json={"booking_date": "2026-10-01"},
        headers=user_auth_headers,
    )

    response = await client.post(
        "/rooms/1/1/booking/",
        json={"booking_date": "2026-10-01"},
        headers=user_auth_headers,
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_user_cannot_delete_other_user_booking(
    client: AsyncClient, user_auth_headers: dict, admin_auth_headers: dict):
    booking_res = await client.post(
        "/rooms/1/1/booking/",
        json={"booking_date": "2026-10-05"},
        headers=admin_auth_headers,
    )
    booking_id = booking_res.json()["id"]

    delete_res = await client.delete(
        f"/rooms/booking/{booking_id}/",
        headers=user_auth_headers,
    )
    assert delete_res.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_delete_any_booking(
    client: AsyncClient, user_auth_headers: dict, admin_auth_headers: dict):
    booking_res = await client.post(
        "/rooms/1/2/booking/",
        json={"booking_date": "2026-10-06"},
        headers=user_auth_headers,
    )
    booking_id = booking_res.json()["id"]

    delete_res = await client.delete(
        f"/rooms/booking/{booking_id}/",
        headers=admin_auth_headers,
    )
    assert delete_res.status_code == 204