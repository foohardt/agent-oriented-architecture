import asyncio
from unittest import IsolatedAsyncioTestCase

from agents import AgentRegistry, RiskAssessmentAgent, TaskAgent
from chromadb.utils import embedding_functions
from config import chroma_client
from knowledge import KnowledgeBase

class TestConcurrentWorkflows(IsolatedAsyncioTestCase):
    async def test_concurrent_workflows(self):
        task_queue = asyncio.Queue()
        risk_queue = asyncio.Queue()

        agent_registry = AgentRegistry()
        agent_registry.register("assess_risk", risk_queue)

        task_agent = TaskAgent(
            "TaskAgent",
            task_queue,
            KnowledgeBase(
                chroma_client.get_collection(
                    "business_rules",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
                )
            ),
            agent_registry,
        )
        risk_agent = RiskAssessmentAgent(
            "RiskAssessmentAgent", risk_queue, agent_registry
        )

        samples = [
            {"name": "John Doe", "risk_level": None, "overdue_days": 120},
            {"name": "Jane Smith", "risk_level": None, "overdue_days": 90},
        ]

        for sample in samples:
            await task_queue.put(sample)

        agents = [
            asyncio.create_task(task_agent.run()),
            asyncio.create_task(risk_agent.run()),
        ]

        await asyncio.sleep(2)

        assert task_queue.empty()
        assert risk_queue.empty()

        for agent in agents:
            agent.cancel()
        await asyncio.gather(*agents, return_exceptions=True)
