# StadiumPulse — Smart Stadium & Tournament Operations for FIFA World Cup 2026

A GenAI-powered multi-agent ecosystem for stadium operations, built for Hack2Skill PromptWars Round 4.

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

## Testing

```bash
# Backend — 52 tests
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