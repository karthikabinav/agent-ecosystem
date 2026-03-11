from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class AgentCreate:
    name: str
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Agent:
    id: str
    name: str
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_create(cls, payload: AgentCreate) -> "Agent":
        now = utcnow()
        return cls(
            id=str(uuid4()),
            name=payload.name,
            status=payload.status,
            metadata=dict(payload.metadata),
            created_at=now,
            updated_at=now,
        )
