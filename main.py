from configparser import ConfigParser
from fastapi import FastAPI
import zulip
from modules.data_structures import TaigaWebhook
from modules.exceptions import EmptyConfigField


cfg = ConfigParser()
cfg.read("config.ini")
if "" in cfg["SETTINGS"]:
    raise EmptyConfigField
stream_name = cfg["SETTINGS"]["STREAM_NAME"]
topic_name = cfg["SETTINGS"]["TOPIC_NAME"]
app = FastAPI()
client = zulip.Client(config_file="zuliprc")


@app.post("/zulip_webhook")
def webhook_endpoint(data: TaigaWebhook):
    if data["action"] != "change" or data["type"] != "task":
        return
    msg = {
        "type": "stream",
        "to": stream_name,
        "topic": topic_name,
        "content": "pricol happend)00))"
    }
    client.send_message(msg)
