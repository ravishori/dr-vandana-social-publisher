from typing import Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator

Platform = Literal[
    "facebook",
    "telegram_channel",
    "telegram_group",
    "whatsapp_channel",
    "whatsapp_group",
]

MediaKind = Literal["image", "video", "document"]

class MediaItem(BaseModel):
    kind: MediaKind
    url: HttpUrl | None = None
    filename: str | None = None
    path: str | None = None

    @field_validator("url", "path", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        if value == "":
            return None
        return value

class PublishRequest(BaseModel):
    message: str = Field(default="", max_length=20000)
    platforms: list[Platform] = Field(min_length=1)
    media: list[MediaItem] = Field(default_factory=list, max_length=10)
    link: HttpUrl | None = None

    @field_validator("message")
    @classmethod
    def message_or_media_required(cls, value):
        return value.strip()

class PublishResult(BaseModel):
    platform: str
    success: bool
    status: str
    provider_message_id: str | None = None
    error: str | None = None
    response: dict | None = None
