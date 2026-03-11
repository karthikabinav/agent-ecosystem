from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import Any

from .models import Agent, AgentCreate, utcnow


class InMemoryAgentStore:
    """Thread-safe in-memory CRUD store for Agent records."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._agents: dict[str, Agent] = {}

    def create(self, payload: AgentCreate) -> Agent:
        with self._lock:
            agent = Agent.from_create(payload)
            self._agents[agent.id] = agent
            return agent

    def get(self, agent_id: str) -> Agent | None:
        with self._lock:
            return self._agents.get(agent_id)

    def list(self) -> list[Agent]:
        with self._lock:
            return list(self._agents.values())

    def update(self, agent_id: str, **fields: Any) -> Agent | None:
        with self._lock:
            current = self._agents.get(agent_id)
            if current is None:
                return None

            allowed = {"name", "status", "metadata"}
            patch = {k: v for k, v in fields.items() if k in allowed}
            if "metadata" in patch and patch["metadata"] is not None:
                patch["metadata"] = dict(patch["metadata"])

            updated = replace(current, **patch, updated_at=utcnow())
            self._agents[agent_id] = updated
            return updated

    def delete(self, agent_id: str) -> bool:
        with self._lock:
            return self._agents.pop(agent_id, None) is not None
