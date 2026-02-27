from redis.asyncio import Redis

redis = Redis.from_url("redis://redis:6379/0")


async def check_redis():
    pong = await redis.ping()
    if pong is not True:
        raise RuntimeError("Redis not reachable")