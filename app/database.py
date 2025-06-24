from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database Base model
Base = declarative_base()

# Database URL
DATABASE_URL = "postgresql+asyncpg://postgres:0.00@localhost/invoice_db"

# Creating the engine for async use
engine = create_async_engine(DATABASE_URL, echo=True)

# Async sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db()-> AsyncSession:
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()