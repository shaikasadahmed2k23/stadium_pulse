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
- **Demo-scale traffic** — rate limiting uses a fixed-window limiter
  (documented limitation in `SECURITY.md`), not a token bucket; assumed
  acceptable for hackathon/demo load, not adversarial production traffic.
- **In-memory state** — cache, incidents, and reasoning logs are
  in-process (not Redis/DB-backed), so state resets on redeploy; assumed
  fine for a single-instance demo deployment (see ADR-002).
- **6 supported languages** (English, Spanish, French, Portuguese,
  Arabic, Hindi) — chosen as a representative subset of FIFA 2026 host
  nations' languages, not an exhaustive list.

## Problem Statement
Smart Stadiums & Tournament Operations — optimizing venue operations and elevating the tournament experience through crowd management, indoor navigation, real-time decision support, and multi-language assistance.

## Architecture

Five specialized agents, one orchestrator:

- **Crowd Intelligence Agent** — live occupancy simulation + congestion prediction
- **Wayfinding Agent** — natural language navigation, congestion-aware routing, low-sensory mode
- **Fan Assistant Agent** — multi-language FAQ + intent routing (text + voice)
- **Anomaly Detector** — proactive incident detection (crowd surges, sustained critical zones)
- **Decision Orchestrator** — aggregates all signals into explainable, prioritized staff recommendations

## Tech Stack

**Backend:** FastAPI, Python 3.11, Gemini 2.5 Flash, LiveKit (voice), Supabase, pytest
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

## Running Locally

**Backend:**
```bash
cd backend
python3.11 -m venv venv
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

## Testing

```bash
# Backend — 67 tests
cd backend && pytest tests/ -v

# Frontend — 12 tests
cd frontend && npm run test
```

## Live Demo

- **Deployed App:** [link after deployment]
- **Control Room Dashboard:** `/control-room`
- **Fan App:** `/fan-app`

## Prompt Workflow / Strategy

Each agent uses a scoped system instruction with Gemini 2.5 Flash, keeping responsibilities narrow (intent detection, route extraction, action generation) rather than one large multi-purpose prompt — this keeps responses fast, predictable, and easy to test independently.