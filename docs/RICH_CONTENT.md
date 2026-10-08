# Rich Content Design

## Supported content package

A publish request can contain:

- message/caption
- optional website/external URL
- zero or more media assets
- one or more destination platforms

Media kinds are currently image, video and document/PDF.

## Provider behavior

### Telegram

Local uploads are sent directly to Telegram using the Bot API:

- image → `sendPhoto`
- video → `sendVideo`
- document/PDF → `sendDocument`
- text/link-only → `sendMessage`

The first media item receives the caption and link. Additional items are sent without repeating the caption.

### Facebook

Text is sent through `/feed`. A single public image/video URL can be sent through the corresponding media endpoint. Local upload paths are rejected for Facebook rather than being incorrectly exposed as public URLs.

### WhatsApp

Not implemented until the exact official Meta capability and account configuration are verified.

## Security

- `.env` is ignored by Git.
- Uploaded files are stored under `uploads/` and ignored by Git.
- Upload size is bounded by `MAX_UPLOAD_SIZE_MB`.
- Filenames are sanitized and replaced with generated UUID names on disk.
- Keep the server bound to `127.0.0.1` during prototype testing.
- Do not expose provider credentials to browser JavaScript.
