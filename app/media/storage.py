from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings

ALLOWED_TYPES = {
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "image/gif": "image",
    "video/mp4": "video",
    "video/quicktime": "video",
    "application/pdf": "document",
}

CHUNK_SIZE = 1024 * 1024


def media_kind(content_type: str | None) -> str:
    if content_type not in ALLOWED_TYPES:
        raise ValueError(
            "Unsupported media type. Allowed: JPEG, PNG, WEBP, GIF, MP4, MOV and PDF."
        )
    return ALLOWED_TYPES[content_type]


async def save_upload(upload: UploadFile) -> dict:
    kind = media_kind(upload.content_type)
    root = Path(settings.upload_dir)
    root.mkdir(parents=True, exist_ok=True)

    original = Path(upload.filename or "upload").name
    suffix = Path(original).suffix.lower()
    target = root / f"{uuid4().hex}{suffix}"
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    total = 0

    try:
        with target.open("wb") as output:
            while True:
                chunk = await upload.read(CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(
                        f"File exceeds MAX_UPLOAD_SIZE_MB={settings.max_upload_size_mb}."
                    )
                output.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return {
        "kind": kind,
        "path": str(target),
        "filename": original,
        "size": total,
        "content_type": upload.content_type,
    }
