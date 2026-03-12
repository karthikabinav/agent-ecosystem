import io
import json
import unittest

from crud_platform import api


class TestApiAgentsListFiltering(unittest.TestCase):
    def setUp(self) -> None:
        api.store = api.InMemoryAgentStore()
        api.store.create(api.AgentCreate(name="planner", status="active"))
        api.store.create(api.AgentCreate(name="researcher", status="paused"))

    def _call(self, path: str, query_string: str = ""):
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = headers

        environ = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": path,
            "QUERY_STRING": query_string,
            "wsgi.input": io.BytesIO(b""),
            "CONTENT_LENGTH": "0",
        }

        body = b"".join(api.app(environ, start_response))
        return captured["status"], json.loads(body or b"{}")

    def test_agents_list_without_filter_returns_all(self):
        status, payload = self._call("/agents")
        self.assertEqual(status, "200 OK")
        self.assertEqual(len(payload["items"]), 2)

    def test_agents_list_with_status_filter(self):
        status, payload = self._call("/agents", "status=paused")
        self.assertEqual(status, "200 OK")
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["status"], "paused")


if __name__ == "__main__":
    unittest.main()
