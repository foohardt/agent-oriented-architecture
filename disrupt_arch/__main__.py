import asyncio
import logging

from agents import AgentRegistry, EscalationAgent, InstallmentPlanAgent, TaskAgent
from chromadb.utils import embedding_functions
from config import chroma_client
from knowledge import KnowledgeBase

logging.basicConfig(level=logging.INFO)


async def main():
    try:
        # Initialize shared components
        agent_registry = AgentRegistry()

        # Define queues
        task_queue = asyncio.Queue()
        escalation_queue = asyncio.Queue()
        payment_queue = asyncio.Queue()

        # Register queues with the registry
        agent_registry.register("escalate", escalation_queue)
        agent_registry.register("payment_plan", payment_queue)

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
            payment_queue,
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

        # Start agents
        asyncio.gather(
            task_agent.run(), escalation_agent.run(), installment_agent.run()
        )

        # Simulate a debtor profile
        debtor_profile = {
            "risk_level": "high",
            "overdue_days": 120,
            "outstanding_balance": 2000,
        }

        await task_queue.put(debtor_profile)

    except Exception as e:
        logging.error(f"A main exception occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
