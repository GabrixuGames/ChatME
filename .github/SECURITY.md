# Security Notes

This project includes security hardening for authentication, SQL access, and message rendering. Keep these guarantees intact.

## Password Hashing (Bcrypt)
- Passwords are hashed with bcrypt on registration.
- Password verification uses bcrypt check during login.
- Never store or log plaintext passwords.

Relevant code:
- `backend/services/auth_service.py`
- `backend/tests/test_password_hashing.py`

## SQL Injection Protection
- All queries use parameterized SQL.
- User-provided IDs are validated (UUID format where applicable).
- Inputs are length-limited and sanitized before querying.

Relevant code:
- `backend/repositories/friend_repository.py`
- `backend/tests/test_sql_injection_fix.py`

## XSS Protection (Frontend)
- User-generated chat content is sanitized before rendering.
- Allowlist-only HTML tags and safe attributes.

Relevant code:
- `frontend/src/components/ChatMessage.tsx`

## JWT and Secrets
- `JWT_SECRET` and `FLASK_SECRET_KEY` are required (min 32 chars).
- Tokens include issuer, audience, and expiration claims.
- Validation verifies signature, issuer, audience, and time claims.

Relevant code:
- `backend/app.py`
- `backend/tests/test_jwt_security.py`

## CORS + Rate Limits
- CORS is allowlist-based and supports custom origins via env vars.
- API rate limits are enabled to reduce abuse and brute-force attempts.

Relevant code:
- `backend/config.py`
- `backend/app.py`
