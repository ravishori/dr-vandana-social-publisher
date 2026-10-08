from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.2.0"


def test_preview_with_link_and_media():
    response = client.post("/api/preview", json={
        "message": "Test article",
        "platforms": ["telegram_channel"],
        "link": "https://example.com/article",
        "media": [{
            "kind": "image",
            "path": "uploads/test.jpg",
            "filename": "test.jpg",
        }],
    })
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["media"][0]["kind"] == "image"


def test_preview_rejects_empty_content():
    response = client.post("/api/preview", json={
        "message": "",
        "platforms": ["telegram_channel"],
    })
    assert response.status_code == 200
    assert response.json()["success"] is False


def test_telegram_caption_splits_oversized_content():
    from app.adapters.telegram import (
        TELEGRAM_CAPTION_LIMIT,
        build_caption_and_remainder,
    )

    message = "Paragraph one.\n\n" + ("Long educational content. " * 80)
    caption, remainder = build_caption_and_remainder(
        message,
        "https://example.com/article",
    )

    assert len(caption) <= TELEGRAM_CAPTION_LIMIT
    assert "https://example.com/article" in caption
    assert remainder
    assert message.split("Paragraph one.", 1)[0] == ""


def test_telegram_text_splitting_respects_4096_limit():
    from app.adapters.telegram import TELEGRAM_MESSAGE_LIMIT, split_text_safely

    text = "A " * 3000
    chunks = split_text_safely(text, TELEGRAM_MESSAGE_LIMIT)

    assert len(chunks) > 1
    assert all(len(chunk) <= TELEGRAM_MESSAGE_LIMIT for chunk in chunks)
    assert " ".join(chunks) == text.strip()
