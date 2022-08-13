from configparser import ConfigParser
from fastapi import FastAPI
import zulip
from modules.data_structures import TaigaWebhook
from modules.exceptions import EmptyConfigField


app = FastAPI()
client = zulip.Client(config_file="zuliprc")


@app.post("/{stream_name}/{topic_name}")
def webhook_endpoint(stream_name: str, topic_name: str, data: TaigaWebhook):
    if data["action"] != "change" or data["type"] != "task":
        return
    msg = {
        "type": "stream",
        "to": stream_name,
        "topic": topic_name,
        "content": "pricol happend)00))"
    }
    client.send_message(msg)
