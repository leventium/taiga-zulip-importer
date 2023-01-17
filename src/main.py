"""
Main module of service where executing starts.
"""
import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from data_structures import TaigaWebhook
from zulip_interface import ZulipInterface
from functions import find_zulip_username_by_slug, create_msg_text_by_data


app = FastAPI()
load_dotenv()
client = None


@app.on_event("startup")
async def start():
    global client
    client = ZulipInterface(
        email=os.environ["BOT_EMAIL"],
        api_key=os.environ["BOT_TOKEN"],
        site=os.environ["ZULIP_URL"]
    )


@app.on_event("shutdown")
async def stop():
    await client.close()


@app.post("/{stream_name}/{topic_name}")
async def webhook_endpoint(stream_name: str,
                           topic_name: str, data: TaigaWebhook):
    data = data.dict()
    stream_name = stream_name.replace("_", " ")
    topic_name = topic_name.replace("_", " ")
    if data["action"] != "change" or data["type"] != "task":
        return

    full_name = await find_zulip_username_by_slug(
        client,
        data["by"]["username"]
    )
    if full_name is not None:
        full_name = f"@_**{full_name}**"
    else:
        full_name = f"**{data['by']['full_name']}**"
    text = await create_msg_text_by_data(data, full_name)

    msg = {
        "type": "stream",
        "to": stream_name,
        "topic": topic_name,
        "content": text
    }
    await client.send_message(msg)


uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
