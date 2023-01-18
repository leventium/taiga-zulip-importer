"""
Main module of service where executing starts.
"""
import os
import uvicorn
import aioredis
from dotenv import load_dotenv
from fastapi import FastAPI
from data_structures import TaigaWebhook
from zulip_interface import ZulipInterface
from caching import get_username_from_cache
from formatting import create_msg_text_by_data


app = FastAPI()
load_dotenv()
client = None
redis = None


@app.on_event("startup")
async def start():
    global client
    global redis
    client = ZulipInterface(
        email=os.environ["BOT_EMAIL"],
        api_key=os.environ["BOT_TOKEN"],
        site=os.environ["ZULIP_URL"]
    )
    redis = aioredis.from_url(
        os.environ["REDIS_CONNSTRING"],
        decode_responses=True
    )


@app.on_event("shutdown")
async def stop():
    await client.close()
    await redis.close()


@app.post("/{stream_name}/{topic_name}")
async def webhook_endpoint(
            stream_name: str,
            topic_name: str,
            data: TaigaWebhook
        ):
    data = data.dict()
    if data["action"] != "change" or data["type"] != "task":
        return
    stream_name = stream_name.replace("_", " ")
    topic_name = topic_name.replace("_", " ")

    full_name = await get_username_from_cache(
        redis,
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
