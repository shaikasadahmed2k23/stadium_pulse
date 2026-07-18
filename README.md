# StadiumPulse — Smart Stadium & Tournament Operations for FIFA World Cup 2026

A GenAI-powered multi-agent ecosystem for stadium operations, built for Hack2Skill PromptWars Round 4.

## Chosen Vertical

**Challenge 4 — Smart Stadiums & Tournament Operations.** StadiumPulse
targets four of the challenge's named personas in one system: fans
(navigation + multilingual assistance), volunteers/venue staff (real-time
decision support), and organizers (operational intelligence + audit
transparency) — built around crowd management, indoor navigation,
accessibility, and multilingual assistance for the FIFA World Cup 2026.

## Approach & Logic

Five narrow, single-responsibility agents instead of one large
multi-purpose assistant — each owns one decision:

- **Crowd Intelligence** classifies zones as normal/elevated/critical from
  occupancy percentage thresholds (70% / 90%) and linearly extrapolates a
  10-minute trend, rather than trying to be a full forecasting model.
- **Wayfinding** takes live congestion output from Crowd Intelligence as
  an input to its BFS pathfinding, so routes actually avoid current
  hotspots instead of routing blind.
- **Anomaly Detector** flags a surge only on a 25%+ occupancy jump *or*
  sustained critical status — tuned to avoid false-positive incident spam
  on every 5-second poll.
- **Decision Orchestrator** aggregates Crowd Intelligence + active
  incidents into prioritized, confidence-scored recommendations, each
  carrying its `reasoning_factors` so staff (and the reasoning-trace
  panel) can see *why*, not just *what*.
- **Fan Assistant** classifies intent first (navigation / ticket /
  general) and routes navigation queries to Wayfinding rather than
  answering them itself — keeps each agent's prompt scoped and testable.

Every agent inherits from a shared `BaseAgent` (`shared/base_agent.py`)
that centralizes Gemini calls, fallback handling, and reasoning logging,
so failure handling and transparency are consistent instead of
reimplemented five times.

## How the Solution Works

1. **Fan-facing:** a fan opens the Fan App, asks a question in any of 6
   languages (text or voice). Fan Assistant classifies intent — FAQ
   queries get answered directly from a lightweight knowledge base +
   Gemini for phrasing; navigation queries get handed to Wayfinding,
   which returns a congestion-aware route (with an optional low-sensory
   mode that avoids high-stimulus zones for accessibility).
2. **Staff-facing:** the Control Room Dashboard polls a WebSocket feed
   (`/ws/control-room`) that pushes live zone occupancy, active
   incidents, and prioritized recommendations every 5 seconds. Anomaly
   Detector runs each cycle and auto-raises incidents before staff would
   otherwise notice; staff can also manually report incidents (lost
   child, medical, security).
3. **Transparency:** every recommendation and every auto-detected
   incident carries its reasoning factors, viewable in a dedicated
   reasoning-trace panel — meant for organizer oversight/audit, not just
   staff action.

See **Architecture** and **Features** below for the full component
breakdown, and `docs/decisions.md` for the reasoning behind specific
technical trade-offs.

## Assumptions Made

- **Simulated sensor data** — no real stadium IoT/turnstile integration
  exists for a hackathon timeline; `features/crowd/sensor_simulator.py`
  generates realistic random-walk occupancy instead.
- **Single-event, single-organizer deployment** — Control Room auth is a
  shared staff API key, not per-user accounts (see `docs/decisions.md`
  ADR-004); assumed acceptable for one event's staff, not a
  multi-tenant SaaS.
- **Demo-scale traffic** — rate limiting uses a custom token-bucket
  limiter (`core/rate_limiter.py`, see `docs/decisions.md` ADR-003), but
  buckets are per-process and keyed by client IP — acceptable for a
  single-instance demo deployment, documented as a known limitation for
  scaling to multi-instance production (see `SECURITY.md`).
- **In-memory state** — cache, incidents, and reasoning logs are
  in-process (not Redis/DB-backed), so state resets on redeploy; assumed
  fine for a single-instance demo deployment (see ADR-002).
- **6 supported languages** (English, Spanish, French, Portuguese,
  Arabic, Hindi) — chosen as a representative subset of FIFA 2026 host
  nations' languages, not an exhaustive list.

## Problem Statement
Smart Stadiums & Tournament Operations — optimizing venue operations and elevating the tournament experience through crowd management, indoor navigation, real-time decision support, and multi-language assistance.

## Architecture

Five specialized agents, one orchestrator — each agent owns a narrow,
single-purpose Gemini prompt (intent detection, route extraction, or
phrasing) rather than one large multi-purpose prompt, keeping responses
fast, predictable, and independently testable.

```text
                     ┌───────────────────────────┐
Fan App / Control     │   FastAPI app (main.py)   │
Room (Next.js) ──────▶│  • CORS + security headers │
                     │  • rate limiting          │
                     └──────────────┬──────────────┘
                                    │
                ┌───────────────────────┼───────────────────────┐
                ▼                       ▼                       ▼
   ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
   │ Crowd Intelligence  │   │  Wayfinding Agent   │   │  Fan Assistant      │
   │ Agent               │   │                     │   │ Agent               │
   │ • occupancy sim     │   │ • congestion-aware   │   │ • intent detection  │
   │ • 10-min prediction │   │   routing (graph)    │   │ • multi-language FAQ│
   │                     │   │ • low-sensory mode   │   │ • routes nav queries│
   └──────────┬───────────┘   └──────────────────────┘   │   to Wayfinding     │
              │                                           └──────────┬─────────┘
              ▼                                                      │
   ┌──────────────────────┐                                          ▼
   │  Anomaly Detector     │                              ┌────────────────────┐
   │ • surge detection     │                              │  Voice Worker       │
   │ • incident intake     │                              │  (LiveKit + Gemini  │
   └──────────┬─────────────┘                              │   Realtime)         │
              │                                              └────────────────────┘
              ▼
   ┌──────────────────────────┐
   │  Decision Orchestrator    │
   │  • aggregates all signals │
   │  • explainable, prioritized│
   │    staff recommendations  │──────▶ Control Room Dashboard (staff/volunteers)
   └────────────────────────────┘
```

Every agent shares one base contract (`shared/base_agent.py`): each call to
Gemini is wrapped in a `log_reasoning()` step that records the factors behind
a decision, so every recommendation shown in the Control Room is traceable
back to the data that produced it — not just a black-box LLM answer.

## Tech Stack

**Backend:** FastAPI, Python 3.12, Gemini 2.5 Flash, LiveKit + Gemini Live Realtime API (voice), Supabase, pytest
**Frontend:** Next.js 14, TypeScript, Tailwind CSS, WebSockets, Vitest + React Testing Library

## Features

1. Crowd Intelligence — live zone occupancy + 10-min prediction
2. Congestion-aware Wayfinding
3. Multi-language Fan Assistant (6 languages)
4. Real-time Decision Support with reasoning transparency
5. Voice-based multi-language assistant
6. Explainable AI — every recommendation shows its reasoning factors
7. Low-sensory routing mode (accessibility)
8. Proactive anomaly detection
9. Offline-first resilience (Fan App)

## Who It Serves

- **Fans** — Fan App: navigation, multi-language chat/voice, low-sensory routing
- **Volunteers & On-Ground Staff** — Control Room Dashboard: real-time zone status, incident alerts, actionable recommendations
- **Organizers** — Reasoning transparency panel gives full visibility into why the system is recommending each action, supporting oversight and audit needs


## Problem Statement Coverage

[Challenge 4: Smart Stadiums & Tournament Operations](#) requires a GenAI-enabled
solution improving venue operations and tournament experience through crowd
management, indoor navigation, real-time decision support, and multi-language
assistance. StadiumPulse maps directly onto these requirements:

| Challenge requirement       | StadiumPulse feature                                              |
| ---------------------------- | ------------------------------------------------------------------ |
| Crowd management             | Crowd Intelligence Agent — live occupancy + 10-min congestion prediction; Anomaly Detector — proactive surge/incident detection |
| Indoor navigation            | Wayfinding Agent — natural-language, congestion-aware routing      |
| Accessibility                | Low-sensory routing mode (avoids high-stimulus zones for sensory-sensitive fans) |
| Multi-language assistance    | Fan Assistant Agent — 6-language FAQ + intent routing, text and voice |
| Real-time decision support   | Decision Orchestrator — aggregates all agent signals into explainable, prioritized staff recommendations |
| Operational intelligence     | Control Room Dashboard — live zone status, incident alerts, reasoning-transparent recommendations for volunteers/staff |

Out of scope for this build (not required for the persona/vertical we chose —
Fans + Volunteers/Staff — see Assumptions Made): dedicated transportation routing
and sustainability tracking modules.

## Running Locally

**Backend:**
```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local  # fill in your values
npm run dev
```

## Project Structure

Backend follows a feature-folder layout — each domain owns its
routes, service logic, and schemas:

```
backend/
  features/
    crowd/          # Feature 1 — occupancy + prediction
    wayfinding/      # Feature 2 + 7 — routing, low-sensory mode
    fan_assistant/   # Feature 3 — chat, FAQ, intent routing
    voice/           # Feature 5 — LiveKit voice sessions
    control_room/    # Feature 4 + 6 + 8 — orchestration, anomalies, WebSocket feed
  shared/           # BaseAgent + cross-feature schemas (ZoneStatus, ZoneData, Language)
  core/             # config, security, rate limiting, error handling — cross-cutting
  services/         # Gemini client, cache, reasoning logger — shared infra
```

See `docs/decisions.md` for the reasoning behind this structure.

## Quality Attributes

### 🔐 Security

- **No secrets in code.** All keys (`GEMINI_API_KEY`, `SUPABASE_KEY`,
  `API_SECRET_KEY`, LiveKit credentials) are read from environment variables
  only; `.env` is git-ignored, only `.env.example` is committed.
- **Input sanitization** on every user-facing text field
  (`core/security.py`) — strips control characters, filters prompt-injection
  patterns, truncates oversized input before it ever reaches Gemini.
- **Security headers** on every response (`core/security_headers.py`):
  `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`,
  Content-Security-Policy, Permissions-Policy.
- **Token-bucket rate limiting** per client/route (`core/rate_limiter.py`),
  returning `429` with `Retry-After` once exhausted.
- **Restrictive CORS** — explicit `ALLOWED_ORIGINS` allow-list, no wildcard.
- **Staff-only endpoints** (Control Room, incident resolution) gated behind
  `API_SECRET_KEY`; Fan App endpoints are public by design.

### ⚡ Efficiency

- **In-memory caching** (`services/cache_service.py`) with TTL avoids
  redundant Gemini calls for repeated queries.
- **Async throughout** — all routes and Gemini calls are non-blocking.
- Voice worker runs as a lightweight subprocess alongside the API process,
  avoiding a separate always-on service on free-tier infrastructure.
- Each Gemini-backed agent uses a **narrow, single-purpose prompt** (intent
  detection, route extraction, phrasing) rather than one large multi-purpose
  prompt — faster responses, easier to test and cache.

### ♿ Accessibility

- **Low-sensory routing mode** — Wayfinding Agent excludes high-stimulus
  zones (loud, crowded, bright) from suggested routes for sensory-sensitive
  fans.
- **Multi-language support** (6 languages) end-to-end for chat and voice,
  so language is never a barrier to getting help.
- **Voice assistant** — hands-free interaction option for fans who find
  typing/reading difficult.
- Frontend uses semantic HTML, labeled form controls, and visible focus
  states throughout (Fan App + Control Room).

### 🧪 Testing

Run the full backend suite:

```bash
cd backend && pytest tests/ --cov=. --cov-report=term-missing -v
```

**99 tests, 95% overall statement coverage**, including full route-level
integration tests (via FastAPI's `TestClient`) for every feature's HTTP
endpoints — not just service-layer unit tests — plus a dedicated WebSocket
feed test for the Control Room live push:

- `test_crowd_agent.py`, `test_sensor_simulator.py`, `test_crowd_routes.py` — occupancy simulation, congestion classification, prediction bounds, HTTP endpoints
- `test_wayfinding_agent.py`, `test_stadium_graph.py`, `test_wayfinding_routes.py` — routing, low-sensory mode, blocked-zone avoidance, HTTP endpoints
- `test_fan_assistant.py`, `test_faq_knowledge.py`, `test_fan_assistant_routes.py` — intent detection, navigation routing, multi-language FAQ matching, HTTP endpoints
- `test_anomaly_detector.py`, `test_decision_orchestrator.py`, `test_incident_store.py`, `test_control_room_routes.py`, `test_control_room_ws.py` — surge detection, reasoning-transparent recommendations, incident lifecycle, staff-key auth (401 on missing/invalid key), live WebSocket feed
- `test_security.py`, `test_security_headers.py`, `test_rate_limiter.py` — input sanitization, prompt-injection filtering, response headers, burst-load limiting
- `test_voice_service.py`, `test_voice_routes.py` — LiveKit session/token generation, HTTP endpoints
- `test_error_handlers.py`, `test_errors.py` — typed error responses, generic-500 fallback
- `test_main_routes.py` — `/health` and `/` root endpoints

**Frontend — 12 tests:**

```bash
cd frontend && npm run test
```

**Lint & types:**

```bash
ruff check .    # All checks passed!
mypy .          # Success: no issues found in 44 source files
```

### 🎯 Code Quality

- `ruff` and `mypy` both pass clean, configured in `backend/pyproject.toml`.
- Each of the 5 agents follows the same `BaseAgent` interface (`shared/base_agent.py`) with structured `log_reasoning()` calls, so every recommendation is explainable and consistent across agents.
- Feature-based folder structure keeps each agent's routes, schemas, and service logic co-located and independently testable.
- Containerized via `Dockerfile` for reproducible builds.

## Live Demo

- **Deployed App:** [https://stadium-pulse-seven.vercel.app](https://stadium-pulse-seven.vercel.app)
- **Backend API:** [https://stadiumpulse-backend-gogf.onrender.com](https://stadiumpulse-backend-gogf.onrender.com)
- **Control Room Dashboard:** `/control-room`
- **Fan App:** `/fan-app`

## Prompt Workflow / Strategy

Each agent uses a scoped system instruction with Gemini 2.5 Flash, keeping responsibilities narrow (intent detection, route extraction, action generation) rather than one large multi-purpose prompt — this keeps responses fast, predictable, and easy to test independently.
