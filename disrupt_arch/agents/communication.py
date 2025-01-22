import logging
from asyncio import Queue

from knowledge import KnowledgeBase
from models import DebtorProfile

from .base import CognitiveAgent
from .registry import AgentRegistry


class CommunicationAgent(CognitiveAgent):
    def __init__(
        self,
        name: str,
        queue: Queue,
        knowledge_base: KnowledgeBase,
        agent_registry: AgentRegistry,
    ):
        super().__init__(name, queue, knowledge_base)
        self.agent_registry = agent_registry
        self.agent_registry.register("contact_debtor", queue)
        self.task = "Your task is to evaluate debtor information and write a personalized message to the debtor to suggest the created payment plan."

    async def process_message(self, entity: DebtorProfile):
        logging.info(f"{self.name} received message: {entity}")
        result = await self.reason_unstructured(
            content=entity.model_dump_json(), task=self.task
        )
        result = await self.reason(entity)
        logging.info(
            f"{self.name} created contanct message for {entity.name}: {result}"
        )
