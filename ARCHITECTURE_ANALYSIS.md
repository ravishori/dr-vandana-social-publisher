# Deep Architecture Analysis

## Goal

Prove a safe multi-platform publishing workflow before modifying the production Dr. Vandana website.

## Architecture

HTML Dashboard
→ FastAPI
→ Publisher Service
→ Platform Adapters
→ Provider APIs

Adapters:
- Telegram
- Facebook
- WhatsApp

## Why standalone?

The existing Dr. Vandana repository has a production engineering baseline with FastAPI/Python, PostgreSQL, modular boundaries, least privilege and auditability. Social publishing should first be validated independently so provider credentials and failures cannot affect production.

## Local placement

Recommended:

D:\ravishori\dr-vandana-social-publisher

as a sibling of:

D:\ravishori\dr-vandana-website

Do not initially put this under the website's `app`, `src`, `public`, or database directories.

## Security

The browser never receives provider tokens.

Correct:

Browser → FastAPI → secret configuration → provider

Prototype binds to 127.0.0.1 only.

Before production:
- authentication
- RBAC
- CSRF strategy
- rate limiting
- audit logging
- secret manager
- retries
- idempotency
- provider error redaction
- monitoring

## Platform assessment

### Telegram

Best first live test. The Telegram Bot API supports sending messages to channels and supergroups when the bot has the necessary permissions.

### Facebook

Requires current Meta Graph API configuration, Page access token and applicable permissions. API versions/permissions can change, so they remain configuration rather than hard-coded assumptions.

### WhatsApp

Do not assume that Channel, Business messaging and Group posting are the same API surface. The prototype intentionally keeps WhatsApp behind a placeholder adapter until the exact official supported destination is verified.

## Content model

Eventually:

Master Article
├── Facebook version
├── WhatsApp version
└── Telegram version

The system should never blindly copy a long Facebook article into every platform.

## Future production entities

- content_articles
- content_variants
- distribution_targets
- distribution_jobs
- distribution_attempts
- distribution_events

Recommended job identity:

article_id + target_id + publication_version

This supports idempotent retries and prevents duplicate publishing.

## Recommended rollout

1. Mock all providers
2. Live Telegram Channel
3. Live Telegram Group
4. Live Facebook Page
5. Verify official WhatsApp capability
6. Integrate service into website CMS
7. Add approval workflow
8. Add scheduling/retries
9. Add controlled automation
