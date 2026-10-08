from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.media.storage import save_upload
from app.models import PublishRequest
from app.services.publisher import PublisherService

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Dr. Vandana Social Publisher", version="0.2.0")
publisher = PublisherService()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "publish_mode": settings.publish_mode,
            "max_message_length": settings.max_message_length,
            "max_upload_size_mb": settings.max_upload_size_mb,
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok", "publish_mode": settings.publish_mode, "version": "0.2.0"}


@app.post("/api/media/upload")
async def upload_media(file: UploadFile = File(...)):
    try:
        result = await save_upload(file)
        return {"success": True, "media": result}
    except ValueError as exc:
        return {"success": False, "error": str(exc)}


@app.post("/api/preview")
async def preview(payload: PublishRequest):
    if not payload.message and not payload.media and not payload.link:
        return {"success": False, "error": "Add text, a link, or media before previewing."}
    if len(payload.message) > settings.max_message_length:
        return {"success": False, "error": "Message exceeds configured limit."}
    return {
        "success": True,
        "message_length": len(payload.message),
        "platforms": payload.platforms,
        "media": [item.model_dump(mode="json") for item in payload.media],
        "link": str(payload.link) if payload.link else None,
        "preview": payload.message,
    }


@app.post("/api/publish")
async def publish(payload: PublishRequest):
    if not payload.message and not payload.media and not payload.link:
        return {"success": False, "error": "Add text, a link, or media before publishing."}
    if len(payload.message) > settings.max_message_length:
        return {"success": False, "error": "Message exceeds configured limit."}

    results = await publisher.publish(payload)
    return {
        "success": all(item.success for item in results),
        "results": [item.model_dump() for item in results],
    }
