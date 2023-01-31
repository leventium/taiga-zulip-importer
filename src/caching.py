"""
Module with caching functions.
"""
async def get_username_from_cache(redis, slug: str) -> str:
    return await redis.hget("users", slug)


async def refrash_usernames_in_caches(redis, data: dict[str, str]) -> None:
    await redis.delete("users")
    await redis.hset("users", mapping=data)
