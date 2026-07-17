# Architecture Decision Records

Short-form ADRs for the non-obvious calls made in this project. Format:
Context → Decision → Trade-off.

---

## ADR-001: Feature-folder structure (superseded a layered structure)

**Context:** The backend has five agents (Crowd, Wayfinding, Fan Assistant,
Anomaly Detector, Decision Orchestrator), each with its own route, schema,
and business logic. The project originally used a layered structure
(`agents/`, `api/`, `core/`, `models/`, `services/`) — fast to navigate
solo during the initial build, but every feature touched 3-4 directories
and `models/schemas.py` was becoming a 140+ line dumping ground.

**Decision:** Migrated to `features/<domain>/{routes, service, schemas}`
— one folder per domain (crowd, wayfinding, fan_assistant, voice,
control_room). Genuinely cross-feature code (BaseAgent, ZoneStatus,
ZoneData, Language) moved to `shared/`; cross-cutting infra (Gemini
client, cache, config, security, rate limiting, error handling) stayed in
`core/`/`services/` since it isn't owned by any one feature.

**Trade-off:** Cross-feature imports now exist (e.g. `wayfinding/service.py`
imports `features.crowd.service.CrowdIntelligenceAgent`, since routing
needs live occupancy data) — this is expected and fine in a feature-folder
layout, not a violation of it. The upside: each feature's routes/service/
schemas sit together, onboarding a reviewer to "how does wayfinding work"
means opening one folder instead of five. Worth doing once the codebase
crossed ~5 domains; would have been premature at 1-2.

---

## ADR-002: In-memory TTL cache, not Redis

**Context:** Gemini calls are the slowest and most rate-limited part of
every request path (crowd summaries, chat responses, wayfinding
explanations).

**Decision:** `services/cache_service.py` wraps `cachetools.TTLCache` —
in-process, thread-locked, 500-entry cap, TTL from `CACHE_TTL_SECONDS`.

**Trade-off:** Cache is per-process and lost on restart/redeploy, and
won't be shared across horizontally-scaled instances. Redis would fix
both, at the cost of a network hop on every cache read and one more
service to provision/monitor. For a single-instance Render deployment at
hackathon scale, the in-process cache's lower latency and zero ops
overhead win. **Swap to Redis if this ever runs as more than one
instance** — the `CacheService` interface (`get`/`set`/`clear`) is
designed so the swap doesn't touch call sites.

---

## ADR-003: Custom token-bucket rate limiter (superseded slowapi's fixed-window)

**Context:** Chat and navigation endpoints need abuse protection against a
single client hammering Gemini (cost) or the routing engine (load). The
project initially used `slowapi` with its default fixed-window counter,
which allows a client to burst up to ~2x the stated limit across a window
boundary (e.g. 20 requests in the last second of one minute + 20 more in
the first second of the next).

**Decision:** Replaced it with a small custom token-bucket implementation
(`core/rate_limiter.py`) — no new dependency needed, ~90 lines. Each
(client, route) pair gets a `TokenBucket` with a capacity (allowed burst)
and a continuous refill rate; `rate_limit(times, per_seconds)` is used as
a FastAPI `Depends()` on rate-limited routes and raises `AppError.rate_limited()`
(handled by the existing global error handler) when a bucket is empty.

**Trade-off:** Buckets are in-process and keyed by client IP (`request.client.host`),
so clients behind a shared NAT/proxy share a bucket, and buckets are never
evicted — both acceptable at hackathon/demo scale (bounded number of
distinct clients hitting a handful of routes), but would need Redis-backed
buckets + TTL eviction before scaling to real production traffic with many
thousands of unique clients.

---

## ADR-004: Shared staff API key, not per-user auth, for Control Room

**Context:** Control Room dashboard is used by a small, known set of
on-ground staff/volunteers during the event.

**Decision:** Single shared `X-API-Key` header checked against
`API_SECRET_KEY` (`core/security.py`), not individual accounts.

**Trade-off:** No per-user audit trail (can't tell *which* staff member
triggered a manual incident report), and the key must be rotated manually
if compromised. Full JWT-based auth (e.g. Supabase Auth) would fix both
but adds login UI, session management, and role modeling that a
single-event hackathon deployment doesn't need yet. Revisit if this
becomes a multi-organizer, multi-event tool.

---

## ADR-005: Gemini 2.5 Flash for every agent, not per-agent model choice

**Context:** Five agents need LLM calls of varying complexity — from
simple intent classification (Fan Assistant routing) to reasoning
summaries (Decision Orchestrator).

**Decision:** Standardize on Gemini 2.5 Flash everywhere, with narrow,
single-purpose system prompts per agent rather than one large multi-tool
prompt or per-agent model tiers.

**Trade-off:** A heavier model (e.g. Gemini 2.5 Pro) might produce
marginally better reasoning-trace explanations for the Decision
Orchestrator, at higher latency and cost. Flash's speed keeps the
control-room feed feeling real-time, which matters more than marginal
reasoning quality for a live-operations tool. Per-agent model tiering is
a reasonable future optimization if the Orchestrator's output quality
becomes a bottleneck.


## ADR-007: Voice Pipeline — Gemini Live RealtimeModel over OpenAI STT/LLM/TTS

**Context:** The original voice worker implementation used OpenAI's separate
STT, LLM, and TTS plugins (`livekit-plugins-openai`) chained together via
`AgentSession`. This required an `OPENAI_API_KEY`, which was never part of
the project's intended stack (Gemini-first across all other agents), and
caused the worker process to crash on startup with a missing-credentials
error.

**Decision:** Replaced the three-stage OpenAI pipeline with Google's
`RealtimeModel` (`livekit-plugins-google`), which handles speech-to-text,
reasoning, and text-to-speech in a single Gemini Live API session. This
keeps the entire project on one LLM provider (Gemini) and one API key,
consistent with every other agent (Crowd Intelligence, Wayfinding, Fan
Assistant).

**Tradeoff:** The Realtime API manages turn detection and transcription
server-side, so the previous custom `on_user_speech_committed` hook (which
routed transcribed text back through `FanAssistantAgent` for FAQ/navigation
intent detection) could not be reused as-is — that logic runs on a
pipeline-agent API, not the Realtime API's event model. For now, the voice
agent answers directly from its own instructions rather than routing
through the text-chat Fan Assistant's FAQ knowledge base and Wayfinding
Agent. Re-integrating that shared intelligence would require passing
`FanAssistantAgent`'s capabilities as function-calling tools to
`RealtimeModel`, which is a follow-up improvement, not required for the
current voice-conversation feature to work end-to-end.