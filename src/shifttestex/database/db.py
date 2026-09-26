from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from shifttestex.database.models import *
import os

database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/shifttestex")
engine = create_async_engine(database_url, echo=False)
session = async_sessionmaker(engine)