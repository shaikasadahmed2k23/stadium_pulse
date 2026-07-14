# Security Policy

## Reporting a Vulnerability

This is a hackathon project (Hack2Skill PromptWars Round 4). If you find a
security issue, please open a GitHub issue tagged `security` or contact the
maintainer directly rather than filing a public PR with exploit details.

## Authentication & Authorization

- **Control Room endpoints** (`/api/control-room/*`) require an `X-API-Key`
  header matched against `API_SECRET_KEY`, verified via
  `core/security.py::verify_staff_api_key`. This is a shared-secret model,
  not per-user auth — acceptable for a single-tenant staff dashboard at
  hackathon scope, but should move to per-user JWTs (e.g. Supabase Auth)
  before any real multi-organizer deployment.
- **Fan-facing endpoints** (chat, navigation, voice session creation) are
  intentionally public — fans aren't expected to authenticate to ask "where's
  the nearest restroom."

## Input Handling

- All free-text fan input (chat, voice transcripts) passes through
  `core/security.py::sanitize_user_input` before reaching Gemini: control
  characters are stripped, length is capped, and common prompt-injection
  phrases (`ignore previous instructions`, `you are now`, etc.) are
  neutralized. This is defense-in-depth, not a guarantee — treat any
  LLM-generated output as untrusted before rendering it or acting on it.

## Rate Limiting — Known Limitation

Rate limiting uses [`slowapi`](https://github.com/laurentS/slowapi)
(`core/rate_limiter.py`), which implements a **fixed-window counter**, not a
token bucket. In practice this means a client can burst up to 2x their limit
across a window boundary (e.g. 20 requests in the last second of one minute
+ 20 in the first second of the next). For this project's scale (hackathon
demo traffic, not production-grade abuse resistance) this is an accepted
trade-off. If this moves toward production, swap to a token-bucket or
sliding-window-log implementation (e.g. `slowapi` with a Redis-backed
sliding window, or `limits` library's `MovingWindowRateLimiter`).

## Data Handling

- No PII is persisted beyond what's needed for incident reports (zone ID,
  description, severity) — no fan identity is required to use the app.
- Supabase credentials and the Gemini API key are loaded from environment
  variables only (`core/config.py`), never committed. See `.env.example`
  for the required variable names.
- LiveKit voice sessions are short-lived, token-scoped per session — see
  `services/voice_service.py`.

## Response Headers

`core/security_headers.py` adds `X-Content-Type-Options`, `X-Frame-Options`,
`Referrer-Policy`, `Permissions-Policy`, a baseline `Content-Security-Policy`,
and HSTS on HTTPS responses. The CSP currently allows `'unsafe-inline'` for
styles to accommodate Tailwind's runtime style injection — see
`docs/decisions.md` for the trade-off and the plan to move to a nonce-based
policy.

## Dependencies

Backend dependencies are pinned in `backend/requirements.txt`. No automated
dependency scanning (e.g. Dependabot, `pip-audit`) is currently wired into
CI — recommended as a follow-up before production use.
