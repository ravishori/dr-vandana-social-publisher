from app.adapters.facebook import FacebookAdapter
from app.adapters.telegram import TelegramAdapter
from app.adapters.whatsapp import WhatsAppAdapter
from app.config import settings
from app.models import PublishResult


class PublisherService:
    def __init__(self):
        self.telegram = TelegramAdapter(settings.telegram_bot_token)
        self.facebook = FacebookAdapter(
            settings.facebook_page_id,
            settings.facebook_page_access_token,
            settings.facebook_graph_api_version,
        )
        self.whatsapp = WhatsAppAdapter()

    async def publish(self, payload):
        results = []
        for platform in payload.platforms:
            if settings.publish_mode == "mock":
                results.append(PublishResult(
                    platform=platform,
                    success=True,
                    status="mock_success",
                    response={
                        "mode": "mock",
                        "media_count": len(payload.media),
                        "link": str(payload.link) if payload.link else None,
                    },
                ))
                continue

            try:
                result = await self._publish_live(platform, payload)
                configured = result.get("status") != "not_configured"
                results.append(PublishResult(
                    platform=platform,
                    success=configured,
                    status="published" if configured else "not_configured",
                    provider_message_id=self._message_id(platform, result),
                    response=result,
                ))
            except Exception as exc:
                results.append(PublishResult(
                    platform=platform,
                    success=False,
                    status="failed",
                    error=str(exc),
                ))
        return results

    async def _publish_live(self, platform, payload):
        media = [item.model_dump(mode="json") for item in payload.media]
        link = str(payload.link) if payload.link else None
        message = payload.message.strip()

        if platform == "telegram_channel":
            return await self.telegram.send_text_and_media(
                settings.telegram_channel_id, message, media, link
            )
        if platform == "telegram_group":
            return await self.telegram.send_text_and_media(
                settings.telegram_group_id, message, media, link
            )

        if link:
            message = f"{message}\n\n{link}" if message else link
        if platform == "facebook":
            return await self._publish_facebook(message, media)
        if platform == "whatsapp_channel":
            return await self.whatsapp.send_message("channel", message, media, link)
        if platform == "whatsapp_group":
            return await self.whatsapp.send_message("group", message, media, link)
        raise ValueError(f"Unsupported platform: {platform}")

    async def _publish_facebook(self, message, media):
        if not media:
            return await self.facebook.publish_text_post(message)

        if len(media) > 1:
            raise RuntimeError(
                "Facebook rich-media multi-upload is not enabled in this prototype. "
                "Use one public image/video URL for now."
            )

        item = media[0]
        if not item.get("url"):
            raise RuntimeError(
                "Facebook media publishing requires a publicly reachable media URL. "
                "A local upload cannot be sent directly by the current Facebook adapter."
            )

        if item["kind"] == "image":
            return await self.facebook.publish_photo_url(message, str(item["url"]))
        if item["kind"] == "video":
            return await self.facebook.publish_video_url(message, str(item["url"]))
        raise RuntimeError("Facebook document publishing is not enabled in this prototype.")

    @staticmethod
    def _message_id(platform, result):
        if platform.startswith("telegram"):
            value = result.get("result", {}).get("message_id")
            if value is not None:
                return str(value)
            results = result.get("results", [])
            if results:
                value = results[0].get("result", {}).get("message_id")
                return str(value) if value is not None else None
        if platform == "facebook":
            value = result.get("id")
            return str(value) if value is not None else None
        return None
