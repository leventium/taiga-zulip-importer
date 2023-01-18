"""
Module with formatting functions.
"""
import re


REGEX_PATTERN = re.compile(r"\\(\S)")


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
        comment = REGEX_PATTERN.sub(r"\1", data["change"]["comment"])
        text = (
            f"**Project:** {project_name}\n"
            f"**Userstory:** {us_name}\n"
            f"**Task:** [{task_name}]({task_link})\n"
            f"**User:** {full_name}\n\n"
            f"```spoiler Комментарий\n{comment}\n```"
        )

    return text
