"""
Module with caching functions.
"""
from zulip_interface import ZulipInterface


async def get_username_from_cache(redis, client: ZulipInterface, slug: str):
    username = await redis.hget("users", slug)
    if username is not None:
        return username
    all_users = await client.get_all_users()
    users_hash = {
        user["email"].split("@")[0]: user["full_name"]
        for user in all_users["members"]
    }
    await redis.delete("users")
    await redis.hset("users", mapping=users_hash)
    return users_hash.get(slug)
