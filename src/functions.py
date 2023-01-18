"""
Module with some functions...
"""
import re
from zulip_interface import ZulipInterface


PATTERN = re.compile(r"\\(\S)")


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


async def create_msg_text_by_data(data: dict, full_name: str):
    project_name = data["data"]["project"]["name"]
    us_name = data["data"]["user_story"]["subject"]
    task_name = data["data"]["subject"]
    task_link = data["data"]["permalink"]

    if data["change"]["diff"] != {}:
        if "status" not in data["change"]["diff"]:
            return
        diff = data["change"]["diff"]["status"]
        text = (
            f"**Project:** {project_name}\n"
            f"**Userstory:** {us_name}\n"
            f"**Task:** [{task_name}]({task_link})\n"
            f"**User:** {full_name}\n\n"
            f"**Изменение статуса:** `{diff['from']}` -> `{diff['to']}`"
        )
    elif data["change"]["comment"] != "":
        if data["change"]["delete_comment_date"] is not None:
            return
        comment = PATTERN.sub(r"\1", data["change"]["comment"])
        text = (
            f"**Project:** {project_name}\n"
            f"**Userstory:** {us_name}\n"
            f"**Task:** [{task_name}]({task_link})\n"
            f"**User:** {full_name}\n\n"
            f"```spoiler Комментарий\n{comment}\n```"
        )

    return text
