"""
Module with caching functions.
"""
import aioredis


class Cache:
    def __init__(self, connstring: str, users_table_name: str) -> None:
        self.users_table_name = users_table_name
        self.redis = aioredis.from_url(connstring, decode_responses=True)

    async def close(self):
        await self.redis.close()

    async def get_name(self, slug: str) -> str:
        return await self.redis.hget(self.users_table_name, slug)

    async def put_hash(self, data: dict[str, str]) -> None:
        await self.redis.delete(self.users_table_name)
        await self.redis.hset(self.users_table_name, mapping=data)
