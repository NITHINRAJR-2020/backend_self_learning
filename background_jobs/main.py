from fastapi import FastAPI , Depends
from model.user_schemas import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.model import user_t
from db.database import getdb , sessionLocal , engine , base
from contextlib import asynccontextmanager
import redis.asyncio as redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    yield

    await app.state.redis.aclose()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


@app.post("/signup")
async def signup_user(user:UserModel , db : AsyncSession = Depends(getdb)):
    new_user = user_t.User(
        id = user.id , 
        name = user.name , 
        age = user.age 
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)