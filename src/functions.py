"""
Module with some functions...
"""
import re
from zulip_interface import ZulipInterface


PATTERN = re.compile(r"\\(\S)")


async def find_zulip_username_by_slug(client: ZulipInterface, slug: str):
    for mail_url in ("@edu.hse.ru", "@miem.hse.ru", "@hse.ru"):
        res = await client.get_user_by_email(slug + mail_url)
        if res is not None:
            return res["user"]["full_name"]


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
