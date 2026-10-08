# Dr. Vandana Social Publisher — Rich Content Prototype v0.3

Standalone FastAPI prototype for controlled multi-platform publishing.

## What's new

- Text publishing remains backward-compatible.
- Upload images, videos and PDFs through the browser.
- Telegram Channel and Group can publish uploaded images, videos and PDFs with captions.
- Add a website/external URL to the caption.
- Add a public image/video URL when the provider can fetch the media directly (currently Facebook).
- Multiple uploaded media files are supported for Telegram by sending them sequentially.
- Telegram oversized captions are automatically split: the media receives a safe caption and remaining content is sent as normal Telegram messages within provider limits.
- Facebook text publishing remains supported.
- Facebook image/video publishing supports a **publicly reachable media URL**; local uploads are intentionally not sent to Facebook yet.
- WhatsApp remains an official-API placeholder. No WhatsApp Web/browser automation is used.
- Mock mode continues to work without sending real posts.

## Important: preserve your working Telegram configuration

Your existing `.env` should contain the signed Telegram IDs:

```env
PUBLISH_MODE=live
TELEGRAM_BOT_TOKEN=your-existing-token
TELEGRAM_CHANNEL_ID=-1004414171897
TELEGRAM_GROUP_ID=-5543829365
```

Do not commit `.env` or expose the bot token.

## Update the existing prototype

1. Stop Uvicorn with `CTRL+C`.
2. Back up your current folder.
3. Extract this ZIP into `D:\ravishori\dr-vandana-social-publisher` and allow files to be replaced.
4. **Do not replace your existing `.env`** with `.env.example`. Keep your current `.env`.
5. From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000`.

## Rich media workflow

1. Enter the caption.
2. Optionally enter the article/website URL.
3. Select one or more images, videos or PDFs.
4. Select the desired channels.
5. Use **Preview** before publishing.
6. Use **Publish Selected**.

### Telegram

Telegram can receive local uploads directly through the Bot API. Images use `sendPhoto`, videos use `sendVideo`, and PDFs use `sendDocument`.

If several media files are selected, this prototype sends them as separate Telegram messages. A later production version can add albums/media groups where appropriate.

### Facebook

Facebook Graph API media publishing generally requires the media to be reachable by the provider. Therefore this version supports a public media URL for photo/video publishing rather than pretending a local browser upload can be sent directly to Facebook.

The production website integration should eventually use its own managed media/CDN storage and pass stable public URLs to platform adapters.

### WhatsApp

WhatsApp Channels, Business messaging and Groups are separate API/product surfaces. The prototype deliberately does not implement unofficial WhatsApp Web automation. We will add only the officially supported capability after the exact Meta account/API configuration is verified.

## Architecture direction

```text
Website CMS
    |
    v
Content Package
    |-- caption
    |-- website URL
    |-- media assets
    |-- selected channels
    v
Distribution Manager
    |---- Telegram Adapter
    |---- Facebook Adapter
    |---- WhatsApp Adapter
    v
Provider APIs
```

The next production iteration should add approval state, distribution history, idempotency, retries, scheduled publishing and platform-specific content variants before connecting this service to the production Dr. Vandana CMS.
