import sys
from datetime import time
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.shifttestex.app.main import app
from src.shifttestex.database.models import Base, Room, TimeSlot, User, UserRole
from src.shifttestex.app.security import create_access_token, password_hash

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db(monkeypatch):
    for mod_name, mod in list(sys.modules.items()):
        if mod and "shifttestex" in mod_name:
            if hasattr(mod, "session"):
                monkeypatch.setattr(mod, "session", TestingSessionLocal)
            if hasattr(mod, "engine"):
                monkeypatch.setattr(mod, "engine", test_engine)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as s:
        ts1_r1 = TimeSlot(id=1, start_time=time(9), end_time=time(11))
        ts2_r1 = TimeSlot(id=2, start_time=time(12), end_time=time(14))

        ts1_r2 = TimeSlot(id=3, start_time=time(9), end_time=time(11))
        ts2_r2 = TimeSlot(id=4, start_time=time(12), end_time=time(14))

        s.add_all([ts1_r1, ts2_r1, ts1_r2, ts2_r2])

        rooms = [
            Room(id=1, name="Комната 1", timeslots=[ts1_r1, ts2_r1]),
            Room(id=2, name="Комната 2", timeslots=[ts1_r2, ts2_r2]),
        ]
        s.add_all(rooms)

        user = User(id=1, username="testuser", hashed_password=password_hash.hash("1234"), role=UserRole.EMPLOYEE)
        admin = User(id=2, username="testadmin", hashed_password=password_hash.hash("admin"), role=UserRole.ADMIN)
        s.add_all([user, admin])

        await s.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def user_auth_headers() -> dict[str, str]:
    user = User(id=1, username="testuser", role=UserRole.EMPLOYEE)
    token = create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def admin_auth_headers() -> dict[str, str]:
    admin = User(id=2, username="testadmin", role=UserRole.ADMIN)
    token = create_access_token(admin)
    return {"Authorization": f"Bearer {token}"}