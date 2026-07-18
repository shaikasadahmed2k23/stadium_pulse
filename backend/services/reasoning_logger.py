"""
Reasoning transparency service (Feature 6). Every agent decision gets
logged with its contributing factors, so the Control Room dashboard
can display *why* a recommendation was made, not just the recommendation.
"""
import logging
import uuid
from datetime import UTC, datetime

logger = logging.getLogger(__name__)

# In-memory store for demo purposes — swap for Supabase table if time allows
_reasoning_store: list[dict] = []


class ReasoningLogger:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    def log(self, decision: str, factors: list[dict]) -> dict:
        entry = {
            "id": str(uuid.uuid4()),
            "agent": self.agent_name,
            "decision": decision,
            "factors": factors,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        _reasoning_store.append(entry)
        logger.info(f"[{self.agent_name}] Reasoning logged: {decision}")
        return entry

    @staticmethod
    def get_recent(limit: int = 20) -> list[dict]:
        return _reasoning_store[-limit:]