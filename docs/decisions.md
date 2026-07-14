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

## ADR-003: Fixed-window rate limiting via slowapi, not token bucket

**Context:** Chat and navigation endpoints need abuse protection against a
single client hammering Gemini (cost) or the routing engine (load).

**Decision:** `slowapi` with its default fixed-window counter
(`core/rate_limiter.py`), applied per-endpoint via `@limiter.limit(...)`.

**Trade-off:** Fixed windows allow a burst of up to ~2x the stated limit
across a window boundary. A token bucket or sliding-window-log would be
smoother, but needs either a custom implementation or a Redis-backed
sliding window (added infra). Documented as an accepted limitation in
`SECURITY.md` rather than solved, given hackathon scope and traffic
profile.

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
