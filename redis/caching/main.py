
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
import json
import asyncio

from db.database import engine , base ,getdb, sessionLocal
from db.model import product_t
from sqlalchemy.ext.asyncio import AsyncSession
from model import product


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


# Fetch product from PostgreSQL
async def loader(p_id: str):
    async with sessionLocal() as db:
        obj = await db.get(product_t.Product, p_id)

        if obj is None:
            return None

        return {
            "product_id": obj.id,
            "p_name": obj.name,
            "p_qty": obj.quantity
        }


# Redis cache-aside with distributed lock
async def fetch_red(loader, p_id: str):

    r = app.state.redis
    key = f"product:{p_id}"

    # 1. Check cache
    value = await r.get(key)

    if value is not None:
        if value == "null":
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                    )
        
        return json.loads(value)

    
    # 2. Acquire distributed lock
    lock = r.lock(f"lock:{key}", timeout=15)

    acquired = await lock.acquire(
        blocking=True,
        blocking_timeout=5
    )

    if not acquired:
        raise HTTPException(
            status_code=503,
            detail="Could not acquire cache lock"
        )

    try:

        # 3. Double-check cache
        value = await r.get(key)

        if value is not None:
            return json.loads(value)

        # 4. Fetch from database
        async with asyncio.timeout(10):
            data = await loader(p_id)

        if data is None:
            await r.set(key , "null" , ex=60)
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # 5. Store in Redis
        await r.set(
            key,
            json.dumps(data),
            ex=300
        )

        return data

    finally:
        await lock.release()


@app.get("/{p_id}")
async def get_product(p_id: str):
    return await fetch_red(loader, p_id)


@app.post("/")
async def post_product(
    obj: product.Product,
    db: AsyncSession = Depends(getdb)
):

    new_product = product_t.Product(
        id=obj.product_id,
        name=obj.p_name,
        quantity=obj.p_qty
    )

    db.add(new_product)

    await db.commit()
    await db.refresh(new_product)

    # Invalidate cache after successful database write
    await app.state.redis.delete(
        f"product:{obj.product_id}"
    )

    return {
        "product_id": new_product.id,
        "p_name": new_product.name,
        "p_qty": new_product.quantity
    }
