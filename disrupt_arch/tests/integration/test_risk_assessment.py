import asyncio
import unittest
from unittest.mock import MagicMock

from agents import AgentRegistry, RiskAssessmentAgent, TaskAgent
from chromadb.utils import embedding_functions
from config import chroma_client
from knowledge import KnowledgeBase
from models import DebtorProfile


class TestRiskAssessmentWorkflow(unittest.IsolatedAsyncioTestCase):
    async def test_risk_assessment_workflow(self):
        agent_registry = AgentRegistry()
        task_queue = asyncio.Queue()
        risk_queue = asyncio.Queue()

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

        risk_assessment_agent = RiskAssessmentAgent(
            "RiskAssessmentAgent", risk_queue, agent_registry
        )

        risk_assessment_agent.execute_task = MagicMock()

        agent_tasks = [
            asyncio.create_task(task_agent.run()),
            asyncio.create_task(risk_assessment_agent.run()),
        ]

        profile = DebtorProfile(
            communication_state="NO_RESPONSE",
            name="John Doe",
            income=50000.0,
            installment_plan=None,
            outstanding_balance=2000.0,
            overdue_days=130,
            risk_level=None,
        )

        await task_queue.put(profile)

        await asyncio.sleep(1)

        risk_assessment_agent.execute_task.assert_called_once()

        for task in agent_tasks:
            task.cancel()
        await asyncio.gather(*agent_tasks, return_exceptions=True)
