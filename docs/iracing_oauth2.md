# iRacing OAuth2 API Reference

Source:
- https://oauth.iracing.com/oauth2/book/authorize_endpoint.html
- https://oauth.iracing.com/oauth2/book/token_endpoint.html

## Client Credentials (from iRacing developer registration)
- `IRACING_CLIENT_ID` — Issued during client registration
- `IRACING_CLIENT_SECRET` — Issued during client registration (required for confidential clients and `password_limited` grant)

## Reference Implementation: irplc (NickBaileyMA/irplc)
A community Python library implementing the `password_limited` grant flow. Key details:

**Env var names used by irplc:**
- `IR_CLIENT_ID`
- `IR_CLIENT_SECRET`
- `IR_USERNAME` (iRacing account email)
- `IR_PASSWORD` (iRacing account password)

**Password/secret masking (`_mask_secret()`):**
1. Lowercase + trim the email (normalized identifier)
2. Concatenate: `secret + normalized_email`
3. SHA-256 hash the result
4. Base64-encode

**Token management:**
- Stores `access_token`, `refresh_token`, `token_expires_at`, `refresh_token_expires_at` as instance variables
- `_ensure_valid_token()` auto-refreshes if expiring within 60s (configurable)
- Refresh uses `grant_type: refresh_token`
- Token URL: POST to iRacing token endpoint with `Content-Type: application/x-www-form-urlencoded`

**Scopes:** default scope is `iracing.auth`

> We will use `IR_*` naming convention for iRacing env vars to stay consistent with irplc.

## /authorize Endpoint

**Required parameters:**
- `client_id`
- `redirect_uri` — Must match exactly what was registered
- `response_type` — Must be `code`

**Recommended/Optional parameters:**
- `code_challenge` — PKCE challenge value; always recommended, required for public clients
- `code_challenge_method` — `S256` (recommended) or `plain`; defaults to `plain`
- `state` — Recommended for CSRF prevention
- `scope` — Space-separated scopes to request
- `prompt` — Supports `"verify"` to disallow stored verifications

## /token Endpoint

### Grant Type 1: Authorization Code
```
grant_type=authorization_code
client_id=...
code=...               (received from redirect_uri)
redirect_uri=...       (must match authorization request)
code_verifier=...      (required if PKCE was used)
client_secret=...      (optional, if issued)
```

### Grant Type 2: Refresh Token
```
grant_type=refresh_token
client_id=...
refresh_token=...
client_secret=...      (optional, if issued)
```

### Grant Type 3: Password Limited
```
grant_type=password_limited
client_id=...
client_secret=...
username=...           (email address)
password=...           (SHA-256 masked — see below)
scope=...              (optional)
```

### Token Response Fields
All grants return JSON:
- `access_token`
- `token_type` — `"Bearer"`
- `expires_in`
- `refresh_token` (optional)
- `refresh_token_expires_in` (optional)
- `scope` (optional)

## Security: Secret & Password Masking
Both `client_secret` and user `password` must be **SHA-256 hashed** before transmission.

**Algorithm:**
1. Normalize the user identifier: trim whitespace and lowercase the email address
2. Concatenate: `secret + normalized_email`
3. SHA-256 hash the concatenated string
4. Base64-encode the result

This applies to both the `client_secret` and the `password` in the `password_limited` grant.

## Notes for Implementation (Milestone 3)
- Use `authorization_code` + PKCE (`S256`) for the standard OAuth2 flow
- Store `access_token`, `refresh_token`, and expiry in memory or a local file (never commit)
- Use `refresh_token` grant to silently renew tokens without re-prompting the user
- `redirect_uri` must be registered with iRacing — for a local bot, this will likely be a `localhost` callback URL
