# Changelog

## v0.3.0 — Telegram caption-limit handling

- Added Telegram-specific caption and message length constants.
- Added safe paragraph/word-aware text splitting.
- Preserved the article URL in the media caption when it fits.
- Automatically sends content exceeding the media-caption limit as follow-up Telegram messages.
- Added validation preventing oversized media captions from reaching the Telegram API.
- Updated the publisher to pass the message and website link separately to the Telegram adapter.
- Added regression tests for oversized captions and long Telegram messages.
