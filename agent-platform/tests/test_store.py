import unittest

from crud_platform.models import AgentCreate
from crud_platform.store import InMemoryAgentStore


class TestInMemoryAgentStore(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryAgentStore()

    def test_crud_roundtrip(self):
        created = self.store.create(AgentCreate(name="planner", metadata={"tier": "core"}))
        self.assertEqual(created.name, "planner")

        fetched = self.store.get(created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, created.id)

        updated = self.store.update(created.id, status="paused")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "paused")

        deleted = self.store.delete(created.id)
        self.assertTrue(deleted)
        self.assertIsNone(self.store.get(created.id))

    def test_list_can_filter_by_status(self):
        self.store.create(AgentCreate(name="planner", status="active"))
        self.store.create(AgentCreate(name="researcher", status="paused"))
        self.store.create(AgentCreate(name="executor", status="active"))

        active = self.store.list(status="active")
        paused = self.store.list(status="paused")

        self.assertEqual(len(active), 2)
        self.assertEqual(len(paused), 1)
        self.assertTrue(all(agent.status == "active" for agent in active))
        self.assertTrue(all(agent.status == "paused" for agent in paused))


if __name__ == "__main__":
    unittest.main()
