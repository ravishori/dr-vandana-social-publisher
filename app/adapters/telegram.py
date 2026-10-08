from pathlib import Path

import httpx


# Telegram Bot API limits captions to 1024 characters and text messages to 4096.
# Keep these as adapter-level constants so every Telegram publishing path uses
# the same limits.
TELEGRAM_CAPTION_LIMIT = 1024
TELEGRAM_MESSAGE_LIMIT = 4096


def split_text_safely(text: str, limit: int) -> list[str]:
    """Split text without exceeding the provider limit.

    Prefer paragraph/newline boundaries, then whitespace, and finally a hard
    character boundary when no natural split point exists.
    """
    text = (text or "").strip()
    if not text:
        return []
    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    chunks: list[str] = []
    remaining = text

    while len(remaining) > limit:
        split_at = remaining.rfind("\n\n", 0, limit + 1)
        if split_at <= 0:
            split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit

        chunk = remaining[:split_at].rstrip()
        if not chunk:
            split_at = limit
            chunk = remaining[:split_at].rstrip()

        chunks.append(chunk)
        remaining = remaining[split_at:].lstrip()

    if remaining:
        chunks.append(remaining)

    return chunks


def build_caption_and_remainder(
    message: str,
    link: str | None = None,
) -> tuple[str, str]:
    """Build a Telegram media caption and return any remaining text.

    The website link is kept in the caption whenever it fits. If the full
    content does not fit, the educational content is split while preserving
    the link in the first caption.
    """
    text = (message or "").strip()
    clean_link = (link or "").strip()

    if clean_link:
        full_text = f"{text}\n\n{clean_link}" if text else clean_link
    else:
        full_text = text

    if len(full_text) <= TELEGRAM_CAPTION_LIMIT:
        return full_text, ""

    if clean_link and len(clean_link) <= TELEGRAM_CAPTION_LIMIT:
        separator = "\n\n"
        available = TELEGRAM_CAPTION_LIMIT - len(clean_link) - len(separator)
        if available > 0:
            prefix_chunks = split_text_safely(text, available)
            prefix = prefix_chunks[0] if prefix_chunks else ""
            caption = f"{prefix}{separator}{clean_link}" if prefix else clean_link
            consumed = len(prefix)
            remainder = text[consumed:].lstrip()
            return caption, remainder

    chunks = split_text_safely(full_text, TELEGRAM_CAPTION_LIMIT)
    caption = chunks[0]
    remainder = "\n\n".join(chunks[1:])
    return caption, remainder


class TelegramAdapter:
    def __init__(self, bot_token: str, timeout: float = 60.0):
        self.bot_token = bot_token
        self.timeout = timeout

    @property
    def base_url(self):
        return f"https://api.telegram.org/bot{self.bot_token}"

    def _check(self, response: httpx.Response):
        if response.is_error:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise RuntimeError(
                f"Telegram API error {response.status_code}: {detail}"
            )
        data = response.json()
        if not data.get("ok", False):
            raise RuntimeError(f"Telegram API error: {data}")
        return data

    async def send_message(self, chat_id: str, message: str) -> dict:
        self._validate(chat_id)
        payload = {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/sendMessage", json=payload)
        return self._check(response)

    async def send_media(
        self,
        chat_id: str,
        kind: str,
        path: str,
        caption: str = "",
    ) -> dict:
        self._validate(chat_id)
        endpoint_map = {
            "image": "sendPhoto",
            "video": "sendVideo",
            "document": "sendDocument",
        }
        field_map = {
            "image": "photo",
            "video": "video",
            "document": "document",
        }
        if kind not in endpoint_map:
            raise ValueError(f"Unsupported Telegram media kind: {kind}")

        if not path:
            raise RuntimeError(
                "Telegram rich media currently requires a local uploaded file. "
                "Use the website/external link field for a normal URL, or upload the media file."
            )

        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(f"Media file not found: {path}")

        data = {"chat_id": chat_id}
        if caption:
            if len(caption) > TELEGRAM_CAPTION_LIMIT:
                raise ValueError(
                    f"Telegram media caption exceeds {TELEGRAM_CAPTION_LIMIT} characters"
                )
            data["caption"] = caption

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            with file_path.open("rb") as media_file:
                response = await client.post(
                    f"{self.base_url}/{endpoint_map[kind]}",
                    data=data,
                    files={field_map[kind]: (file_path.name, media_file)},
                )
        return self._check(response)

    async def send_text_and_media(
        self,
        chat_id: str,
        message: str,
        media: list[dict],
        link: str | None = None,
    ) -> dict:
        text = message.strip()

        if not media:
            full_text = f"{text}\n\n{link}" if text and link else (link or text)
            chunks = split_text_safely(full_text, TELEGRAM_MESSAGE_LIMIT)
            results = [await self.send_message(chat_id, chunk) for chunk in chunks]
            if not results:
                return {"ok": True, "results": []}
            return results[0] if len(results) == 1 else {"ok": True, "results": results}

        caption, remainder = build_caption_and_remainder(text, link)

        results = []
        for index, item in enumerate(media):
            item_caption = caption if index == 0 else ""
            result = await self.send_media(
                chat_id=chat_id,
                kind=item["kind"],
                path=item["path"],
                caption=item_caption,
            )
            results.append(result)

        # Any content that did not fit into the media caption is delivered as
        # one or more normal Telegram text messages, respecting the 4096 limit.
        for chunk in split_text_safely(remainder, TELEGRAM_MESSAGE_LIMIT):
            results.append(await self.send_message(chat_id, chunk))

        return results[0] if len(results) == 1 else {"ok": True, "results": results}

    @staticmethod
    def _validate(chat_id: str):
        if not chat_id:
            raise RuntimeError("Telegram destination ID is not configured")
