import httpx


class ZulipInterface:
    def __init__(self, email: str, api_key: str, site: str) -> None:
        self.client = httpx.AsyncClient(base_url=site, auth=(email, api_key))
    
    async def close(self) -> None:
        await self.client.aclose()
    
    async def send_message(self, msg: dict[str, str]) -> None:
        await self.client.post("/api/v1/messages", params=msg)
