# agent-platform

First executable CRUD code slice for agent records.

## Scope

- `crud_platform/models.py` — typed data models (`AgentCreate`, `Agent`)
- `crud_platform/store.py` — thread-safe in-memory CRUD storage
- `crud_platform/api.py` — minimal local HTTP API (WSGI; stdlib-only)
- `tests/test_store.py` — unittest stub for CRUD roundtrip

## Run tests

```bash
cd agent-platform
PYTHONPATH=. python -m unittest -v
```

## Run API locally

```bash
cd agent-platform
PYTHONPATH=. python -m crud_platform.api
```

Quick smoke test:

```bash
curl -s http://127.0.0.1:8080/health
curl -s -X POST http://127.0.0.1:8080/agents -H 'content-type: application/json' -d '{"name":"planner"}'
curl -s http://127.0.0.1:8080/agents
```
