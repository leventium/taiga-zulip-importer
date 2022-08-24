from configparser import ConfigParser
from typing import List
from fastapi import FastAPI, APIRouter
import zulip
from modules.data_structures import TaigaWebhook
from modules.exceptions import EmptyConfigField


def remove_symbols(text: str, symbols: List[str]) -> str:
    for c in symbols:
        text = text.replace(f"\\{c}", f"{c}")
    return text


cfg = ConfigParser()
cfg.read("config.ini")
if "" in cfg["SETTINGS"].values():
    raise EmptyConfigField()
router = APIRouter(prefix=cfg["SETTINGS"]["ROOT_PATH"].rstrip("/"))
symbols = cfg["SETTINGS"]["SPECIAL_SYMBOLS"].split()
app = FastAPI()
client = zulip.Client(config_file="zuliprc")


@router.post("/{stream_name}/{topic_name}")
def webhook_endpoint(stream_name: str, topic_name: str, data: TaigaWebhook):
    data = data.dict()
    stream_name = stream_name.replace("_", " ")
    topic_name = topic_name.replace("_", " ")
    if data["action"] != "change" or data["type"] != "task":
        return

    project_name = data["data"]["project"]["name"]
    initiator_full_name = data["by"]["full_name"]
    us_name = data["data"]["user_story"]["subject"]
    task_name = data["data"]["subject"]

    if data["change"]["diff"] != {}:
        if "status" not in data["change"]["diff"]:
            return
        diff = data["change"]["diff"]["status"]
        text = (
            f"**Project:** {project_name}\n"
            f"**Userstory:** {us_name}\n"
            f"**Task:** {task_name}\n"
            f"**User:** @_**{initiator_full_name}**\n\n"
            f"**Изменение статуса:** `{diff['from']}` -> `{diff['to']}`"
        )
    elif data["change"]["comment"] != "":
        if data["change"]["delete_comment_date"] is not None:
            return
        comment = remove_symbols(data["change"]["comment"], symbols)
        text = (
            f"**Project:** {project_name}\n"
            f"**Userstory:** {us_name}\n"
            f"**Task:** {task_name}\n"
            f"**User:** @_**{initiator_full_name}**\n\n"
            f"```spoiler Комментарий\n{comment}\n```"
        )

    msg = {
        "type": "stream",
        "to": stream_name,
        "topic": topic_name,
        "content": text
    }
    client.send_message(msg)


app.include_router(router)
