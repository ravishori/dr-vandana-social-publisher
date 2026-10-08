# Production Integration Plan

1. Standalone prototype
2. Validate Telegram
3. Validate Facebook
4. Verify official WhatsApp capabilities
5. Move reusable adapters into the website backend
6. Add CMS distribution checkboxes
7. Add platform-specific content variants
8. Add distribution jobs and attempts
9. Add scheduling/retries/idempotency
10. Add controlled automation

Recommended future CMS flow:

Article
→ Preview
→ Select channels
→ Approve
→ Publish
→ Track per-channel result

Do not connect the prototype directly to the production database.
