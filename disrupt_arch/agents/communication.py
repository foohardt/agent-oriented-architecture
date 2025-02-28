import asyncio
import logging

from knowledge import KnowledgeBase
from models import DebtorProfile

from .base import CognitiveAgent
from .registry import AgentRegistry


class CommunicationAgent(CognitiveAgent):
    def __init__(
        self,
        name: str,
        queue: asyncio.Queue,
        knowledge_base: KnowledgeBase,
        agent_registry: AgentRegistry,
    ):
        super().__init__(name, queue, knowledge_base)
        self.agent_registry = agent_registry
        self.agent_registry.register("contact_debtor", queue)
        self.task = "Your task is to evaluate debtor information and write a personalized message to the debtor to suggest the created payment plan."

    async def process_message(self, entity: DebtorProfile):
        try:
            logging.info(f"{self.name} received message: {entity}")

            reasoning_task = asyncio.create_task(
                self.reason_unstructured(
                    content=entity.model_dump_json(), task=self.task
                )
            )

            result = await reasoning_task

            logging.info(
                f"{self.name} created contact message for {entity.name}: {result}"
            )

        except Exception as e:
            logging.error(f"{self.name} encountered an exception: {e}")
