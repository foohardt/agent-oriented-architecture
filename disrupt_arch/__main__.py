import asyncio
import logging

from agents import (
    AgentRegistry,
    CommunicationAgent,
    EscalationAgent,
    InstallmentPlanAgent,
    RiskAssessmentAgent,
    TaskAgent,
)
from chromadb.utils import embedding_functions
from config import chroma_client
from knowledge import KnowledgeBase
from models import DebtorProfile

logging.basicConfig(level=logging.INFO)


async def main():
    try:
        # Initialize shared components
        agent_registry = AgentRegistry()

        # Define queues
        task_queue = asyncio.Queue()
        escalation_queue = asyncio.Queue()
        risk_assessment_queue = asyncio.Queue()
        installment_plan_queue = asyncio.Queue()
        debtor_communication_queue = asyncio.Queue()

        # Register queues with the registry
        agent_registry.register("escalate", escalation_queue)
        agent_registry.register("installment_plan", installment_plan_queue)

        # Define agents
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

        communication_agent = CommunicationAgent(
            "CommunicationAgent",
            debtor_communication_queue,
            KnowledgeBase(
                chroma_client.get_collection(
                    "business_rules",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
                )
            ),
            agent_registry,
        )

        escalation_agent = EscalationAgent(
            "EscalationAgent", escalation_queue, agent_registry
        )

        risk_assessment_agent = RiskAssessmentAgent(
            "RiskAssessmentAgent", risk_assessment_queue, agent_registry
        )

        asyncio.gather(
            task_agent.run(),
            escalation_agent.run(),
            installment_agent.run(),
            risk_assessment_agent.run(),
            communication_agent.run(),
        )

        debtor_profile = DebtorProfile(
            communication_state="NO_RESPONSE",
            income=50000,
            installment_plan=None,
            risk_level=None,
            overdue_days=120,
            outstanding_balance=2000.0,
            name="John Doe",
        )
        await task_queue.put(debtor_profile)

        await asyncio.Event().wait()

    except Exception as e:
        logging.error(f"A main exception occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
