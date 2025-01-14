import logging
from asyncio import Queue

from config import openai_client
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

    async def process_message(self, entity: DebtorProfile):
        logging.info(f"{self.name} received profile: {entity}")
        result = await self.reason(entity)
        logging.info(f"{self.name} created message for {entity.name}: {result}")

    async def reason(self, entity: DebtorProfile):
        prompt = f"""
        debtor profile: {entity},
        """
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "developer",
                        "content": "You are a debt collection assistant. Your task is to evaluate debtor information and write a personalized message to the debtor to suggest the created payment plan.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            message = completion.choices[0].message

            return message
        except Exception as e:
            logging.error(f"Error reasoning debtor communication: {e}")
