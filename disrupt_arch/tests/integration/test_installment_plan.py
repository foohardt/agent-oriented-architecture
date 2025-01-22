import asyncio
import unittest
from unittest.mock import AsyncMock

from agents import (
    AgentRegistry,
    CommunicationAgent,
    InstallmentPlanAgent,
    RiskAssessmentAgent,
    TaskAgent,
)
from chromadb.utils import embedding_functions
from config import chroma_client
from knowledge import KnowledgeBase
from models import DebtorProfile, InstallmentPlan


class TestInstallmentPlan(unittest.IsolatedAsyncioTestCase):
    async def test_installment_plan_workflow(self):
        agent_registry = AgentRegistry()
        task_queue = asyncio.Queue()
        risk_queue = asyncio.Queue()
        installment_plan_queue = asyncio.Queue()
        communication_queue = asyncio.Queue()

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

        installment_agent = InstallmentPlanAgent(
            "InstallmentPlanAgent",
            installment_plan_queue,
            KnowledgeBase(
                chroma_client.get_collection(
                    "business_rules",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
                )
            ),
            agent_registry,
        )
        installment_agent.reason_structured = AsyncMock(
            return_value={
                "action": "contact_debtor",
                "installment_plan": InstallmentPlan(
                    monthly_payment=50, duration_months=12
                ),
            }
        )

        communication_agent = CommunicationAgent(
            "CommunicationAgent",
            communication_queue,
            KnowledgeBase(
                chroma_client.get_collection(
                    "business_rules",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
                )
            ),
            agent_registry,
        )
        communication_agent.reason_unstructured = AsyncMock(
            return_value="This is a mocked debtor contact message."
        )

        profile = DebtorProfile(
            communication_state="NO_RESPONSE",
            name="John Doe",
            income=50000.0,
            installment_plan=None,
            outstanding_balance=2000.0,
            overdue_days=20,
            risk_level=None,
        )

        agent_tasks = [
            asyncio.create_task(task_agent.run()),
            asyncio.create_task(risk_assessment_agent.run()),
            asyncio.create_task(installment_agent.run()),
            asyncio.create_task(communication_agent.run()),
        ]

        await task_queue.put(profile)

        await asyncio.sleep(2)

        installment_agent.reason_structured.assert_called_once()
        communication_agent.reason_unstructured.assert_awaited_once()

        for task in agent_tasks:
            task.cancel()
        await asyncio.gather(*agent_tasks, return_exceptions=True)
