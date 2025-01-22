import logging
from asyncio import Queue

from knowledge import KnowledgeBase
from models import DebtorProfile, NextBestAction

from .base import CognitiveAgent
from .registry import AgentRegistry


class TaskAgent(CognitiveAgent):
    def __init__(
        self,
        name: str,
        queue: Queue,
        knowledge_base: KnowledgeBase,
        agent_registry: AgentRegistry,
    ):
        super().__init__(name, queue, knowledge_base)
        self.agent_registry = agent_registry
        self.agent_registry.register("next_action", queue)
        self.task = "Your task is to evaluate debtor information and determine the next best action based on the provided business rules."

    async def process_message(self, entity: DebtorProfile):
        logging.info(f"{self.name} received message: {entity}")
        business_rules = await self.retrieve(entity)

        content = f"debtor profile: {entity}, business rules: {business_rules}"
        next_action = await self.reason_structured(
            content=content, response_format=NextBestAction, task=self.task
        )
        logging.info(f"{self.name} decided next action: {next_action}")

        target_queues = self.agent_registry.get_agents_for_task(next_action.action)
        await self.publish_message(target_queues, entity)

    async def retrieve(self, entity: DebtorProfile):
        try:
            query = f"Risk level is {entity.risk_level} and overdue days is {
                entity.overdue_days
            }."
            rules = await self.query_knowledge(query)
            return rules
        except Exception as e:
            logging.error(f"Error retrieving business rules: {e}")
