from configparser import ConfigParser
from fastapi import FastAPI, APIRouter
import zulip
from modules.data_structures import TaigaWebhook
from modules.exceptions import EmptyConfigField


cfg = ConfigParser()
cfg.read("config.ini")
if "" in cfg["SETTINGS"].values():
    raise EmptyConfigField()
router = APIRouter(prefix=cfg["SETTINGS"]["ROOT_PATH"].rstrip("/"))
app = FastAPI()
client = zulip.Client(config_file="zuliprc")


@router.post("/{stream_name}/{topic_name}")
def webhook_endpoint(stream_name: str, topic_name: str, data: TaigaWebhook):
    data = data.dict()
    stream_name = " ".join(stream_name.split("_"))
    topic_name = " ".join(topic_name.split("_"))
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
            f"**Task:** {task_name}\n\n"
            f"@_**{initiator_full_name}** изменил статус задачи с "
            f"**{diff['from']}** на **{diff['to']}**."
        )
    elif data["change"]["comment"] != "":
        comment = data["change"]["comment"]
        text = (
            f"**Project:** {project_name}\n"
            f"**Userstory:** {us_name}\n"
            f"**Task:** {task_name}\n\n"
            f"**Комментарий от** @_**{initiator_full_name}**:\n"
            f"```spoiler\n{comment}\n```"
        )

    msg = {
        "type": "stream",
        "to": stream_name,
        "topic": topic_name,
        "content": text
    }
    client.send_message(msg)


app.include_router(router)
