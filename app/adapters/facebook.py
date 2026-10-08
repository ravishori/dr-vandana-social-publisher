import httpx


class FacebookAdapter:
    def __init__(self, page_id, access_token, graph_api_version, timeout=60.0):
        self.page_id = page_id
        self.access_token = access_token
        self.graph_api_version = graph_api_version
        self.timeout = timeout

    @property
    def base_url(self):
        return f"https://graph.facebook.com/{self.graph_api_version}/{self.page_id}"

    def _validate(self):
        if not self.page_id:
            raise RuntimeError("FACEBOOK_PAGE_ID is not configured")
        if not self.access_token:
            raise RuntimeError("FACEBOOK_PAGE_ACCESS_TOKEN is not configured")

    def _check(self, response: httpx.Response):
        if response.is_error:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise RuntimeError(
                f"Facebook Graph API error {response.status_code}: {detail}"
            )
        return response.json()

    async def publish_text_post(self, message: str) -> dict:
        self._validate()
        payload = {"message": message, "access_token": self.access_token}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/feed", data=payload)
        return self._check(response)

    async def publish_photo_url(self, message: str, media_url: str) -> dict:
        self._validate()
        payload = {
            "url": media_url,
            "caption": message,
            "access_token": self.access_token,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/photos", data=payload)
        return self._check(response)

    async def publish_video_url(self, message: str, media_url: str) -> dict:
        self._validate()
        payload = {
            "file_url": media_url,
            "description": message,
            "access_token": self.access_token,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/videos", data=payload)
        return self._check(response)
