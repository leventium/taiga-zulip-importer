import os
import re
import zulip
import uvicorn
from fastapi import FastAPI
from data_structures import TaigaWebhook


app = FastAPI()
PATTERN = re.compile(r"\\(\S)")
client = zulip.Client(
    email=os.environ["BOT_EMAIL"],
    api_key=os.environ["BOT_TOKEN"],
    site=os.environ["ZULIP_URL"]
)


@app.post("/{stream_name}/{topic_name}")
def webhook_endpoint(stream_name: str, topic_name: str, data: TaigaWebhook):
    data = data.dict()
    stream_name = stream_name.replace("_", " ")
    topic_name = topic_name.replace("_", " ")
    if data["action"] != "change" or data["type"] != "task":
        return

    name_list = data["by"]["full_name"].split()
    match len(name_list):
        case 3:
            initiator_full_name = (
                f"@_**{' '.join([name_list[1], name_list[0]])}**"
            )
        case 2:
            initiator_full_name = f"@_**{data['by']['full_name']}**"
        case _:
            initiator_full_name = f"**{data['by']['full_name']}**"

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
            f"**User:** {initiator_full_name}\n\n"
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
            f"**User:** {initiator_full_name}\n\n"
            f"```spoiler Комментарий\n{comment}\n```"
        )

    msg = {
        "type": "stream",
        "to": stream_name,
        "topic": topic_name,
        "content": text
    }
    client.send_message(msg)


uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
