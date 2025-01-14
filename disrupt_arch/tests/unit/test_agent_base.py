import asyncio
import unittest

from agents.base.agent import Agent
from models import DebtorProfile


class TestAgent(Agent):
    def __init__(self, name: str, queue: asyncio.Queue):
        super().__init__(name, queue)
        self.processed_messages = []

    async def process_message(self, profile: DebtorProfile):
        """Mock implementation of the abstract method."""
        self.processed_messages.append(profile)


class TestAgentBase(unittest.IsolatedAsyncioTestCase):
    async def test_run_processes_messages(self):
        test_queue = asyncio.Queue()
        agent = TestAgent("TestAgent", test_queue)

        profile = DebtorProfile(
            communication_state="ENGAGED",
            name="Alice",
            income=30000.0,
            installment_plan=None,
            outstanding_balance=500.0,
            overdue_days=60,
            risk_level="LOW",
        )

        await test_queue.put(profile)

        task = asyncio.create_task(agent.run())
        await asyncio.sleep(0.1)
        task.cancel()

        self.assertIn(profile, agent.processed_messages)
        self.assertEqual(len(agent.processed_messages), 1)

    async def test_publish_message(self):
        target_queue = asyncio.Queue()
        agent = TestAgent("TestAgent", target_queue)

        profile = DebtorProfile(
            communication_state="ENGAGED",
            name="Alice",
            income=30000.0,
            installment_plan=None,
            outstanding_balance=500.0,
            overdue_days=60,
            risk_level="LOW",
        )

        await agent.publish_message([target_queue], profile)

        self.assertEqual(await target_queue.get(), profile)
        self.assertEqual(target_queue.qsize(), 0)
