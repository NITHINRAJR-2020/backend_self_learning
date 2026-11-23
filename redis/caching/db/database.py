from sqlalchemy.ext.asyncio import async_sessionmaker , create_async_engine
from sqlalchemy.orm import declarative_base
from core.config import Config
database_url = Config.DATABASE_URL

engine = create_async_engine(
    url=database_url,
    echo=True
)

sessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def getdb():
    async with sessionLocal() as db:
        yield db

base = declarative_base()