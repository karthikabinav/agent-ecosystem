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


if __name__ == "__main__":
    unittest.main()
