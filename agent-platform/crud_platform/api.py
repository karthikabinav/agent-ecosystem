from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from http import HTTPStatus
from wsgiref.simple_server import make_server

from .models import AgentCreate
from .store import InMemoryAgentStore

store = InMemoryAgentStore()


def _to_json_bytes(payload: object) -> bytes:
    def default(obj: object) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    return json.dumps(payload, default=default).encode("utf-8")


def app(environ, start_response):
    method = environ["REQUEST_METHOD"]
    path = environ["PATH_INFO"]

    if path == "/health" and method == "GET":
        body = _to_json_bytes({"ok": True})
        start_response(f"{HTTPStatus.OK.value} OK", [("Content-Type", "application/json")])
        return [body]

    if path == "/agents" and method == "GET":
        agents = [asdict(a) for a in store.list()]
        body = _to_json_bytes({"items": agents})
        start_response(f"{HTTPStatus.OK.value} OK", [("Content-Type", "application/json")])
        return [body]

    if path == "/agents" and method == "POST":
        try:
            raw = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))
            data = json.loads(raw or b"{}")
            agent = store.create(AgentCreate(name=data["name"], status=data.get("status", "active"), metadata=data.get("metadata", {})))
            body = _to_json_bytes(asdict(agent))
            start_response(f"{HTTPStatus.CREATED.value} Created", [("Content-Type", "application/json")])
            return [body]
        except (KeyError, json.JSONDecodeError):
            body = _to_json_bytes({"error": "Invalid payload; expected JSON with required field 'name'."})
            start_response(f"{HTTPStatus.BAD_REQUEST.value} Bad Request", [("Content-Type", "application/json")])
            return [body]

    if path.startswith("/agents/"):
        agent_id = path.split("/", 2)[2]

        if method == "GET":
            agent = store.get(agent_id)
            if agent is None:
                start_response(f"{HTTPStatus.NOT_FOUND.value} Not Found", [("Content-Type", "application/json")])
                return [_to_json_bytes({"error": "Agent not found"})]
            start_response(f"{HTTPStatus.OK.value} OK", [("Content-Type", "application/json")])
            return [_to_json_bytes(asdict(agent))]

        if method == "PATCH":
            try:
                raw = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))
                patch = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                start_response(f"{HTTPStatus.BAD_REQUEST.value} Bad Request", [("Content-Type", "application/json")])
                return [_to_json_bytes({"error": "Invalid JSON payload"})]

            agent = store.update(agent_id, **patch)
            if agent is None:
                start_response(f"{HTTPStatus.NOT_FOUND.value} Not Found", [("Content-Type", "application/json")])
                return [_to_json_bytes({"error": "Agent not found"})]

            start_response(f"{HTTPStatus.OK.value} OK", [("Content-Type", "application/json")])
            return [_to_json_bytes(asdict(agent))]

        if method == "DELETE":
            deleted = store.delete(agent_id)
            if not deleted:
                start_response(f"{HTTPStatus.NOT_FOUND.value} Not Found", [("Content-Type", "application/json")])
                return [_to_json_bytes({"error": "Agent not found"})]
            start_response(f"{HTTPStatus.NO_CONTENT.value} No Content", [("Content-Type", "application/json")])
            return [b""]

    start_response(f"{HTTPStatus.NOT_FOUND.value} Not Found", [("Content-Type", "application/json")])
    return [_to_json_bytes({"error": "Not Found"})]


if __name__ == "__main__":
    with make_server("127.0.0.1", 8080, app) as server:
        print("CRUD API listening on http://127.0.0.1:8080")
        server.serve_forever()
