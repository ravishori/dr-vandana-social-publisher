import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    publish_mode: str = os.getenv("PUBLISH_MODE", "mock").lower()
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_channel_id: str = os.getenv("TELEGRAM_CHANNEL_ID", "")
    telegram_group_id: str = os.getenv("TELEGRAM_GROUP_ID", "")
    facebook_page_id: str = os.getenv("FACEBOOK_PAGE_ID", "")
    facebook_page_access_token: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    facebook_graph_api_version: str = os.getenv("FACEBOOK_GRAPH_API_VERSION", "vXX.X")
    whatsapp_access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    whatsapp_api_version: str = os.getenv("WHATSAPP_API_VERSION", "vXX.X")
    max_message_length: int = _int_env("MAX_MESSAGE_LENGTH", 4000)
    max_upload_size_mb: int = _int_env("MAX_UPLOAD_SIZE_MB", 50)
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")


settings = Settings()
