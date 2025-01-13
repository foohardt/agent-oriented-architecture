import asyncio
import unittest
from unittest.mock import MagicMock
from agents import AgentRegistry, EscalationAgent,TaskAgent, RiskAssessmentAgent
from knowledge import KnowledgeBase
from models import DebtorProfile
from config import chroma_client
from chromadb.utils import embedding_functions


class TestEscalationWorkflow(unittest.IsolatedAsyncioTestCase):
    async def test_task_to_risk_assessment_flow(self):
        agent_registry = AgentRegistry()
        task_queue = asyncio.Queue()
        risk_queue = asyncio.Queue()

        escalation_queue = asyncio.Queue()


        agent_registry.register("escalate_case", escalation_queue)


        task_agent = TaskAgent(
            "TaskAgent",
            task_queue,
                        KnowledgeBase(
                chroma_client.get_collection(
                    "business_rules",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
                )
            ),
            agent_registry)


        escalation_agent = EscalationAgent(
            "EscalationAgent", escalation_queue, agent_registry
        )
        escalation_agent.execute_task = MagicMock()

        risk_assessment_agent = RiskAssessmentAgent(
            "RiskAssessmentAgent", risk_queue, agent_registry
        )


        agent_tasks = [
            asyncio.create_task(task_agent.run()),
            asyncio.create_task(risk_assessment_agent.run()),
            asyncio.create_task(escalation_agent.run()),
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

        escalation_agent.execute_task.assert_called_once()

        for task in agent_tasks:
            task.cancel()
        await asyncio.gather(*agent_tasks, return_exceptions=True)
