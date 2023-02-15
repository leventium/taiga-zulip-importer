"""
Module with Zulip interface.
"""
import httpx


class ZulipInterface:
    """
    Class that provides abstraction under zulip API.
    """
    def __init__(self, email: str, api_key: str, site: str) -> None:
        self.client = httpx.AsyncClient(base_url=site, auth=(email, api_key))

    async def close(self) -> None:
        await self.client.aclose()

    async def send_message(self, msg: dict[str, str]) -> None:
        await self.client.post("/api/v1/messages", params=msg)

    async def get_user_by_email(self, email: str) -> dict | None:
        res = await self.client.get(f"/api/v1/users/{email}")
        return res.json() if res.status_code == 200 else None

    async def get_all_users(self) -> dict | None:
        res = await self.client.get("/api/v1/users")
        return res.json() if res.status_code == 200 else None
