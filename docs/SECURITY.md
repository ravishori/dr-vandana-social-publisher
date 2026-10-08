# Security

Never commit `.env` or provider tokens.

Never put provider tokens in HTML/JavaScript.

Prototype binding should remain:

127.0.0.1:8000

Before production integration, implement:
- authenticated admin access
- RBAC
- CSRF protection appropriate to auth model
- secret management
- rate limiting
- audit logging
- retry classification
- idempotency
- monitoring
- provider error redaction

Never test with patient/client information.
