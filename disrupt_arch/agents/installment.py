import asyncio
import logging

from knowledge import KnowledgeBase
from models import DebtorProfile, InstallmentPlan

from .base import CognitiveAgent
from .registry import AgentRegistry


class InstallmentPlanAgent(CognitiveAgent):
    def __init__(
        self, name, queue, knowledge_base: KnowledgeBase, agent_registry: AgentRegistry
    ):
        super().__init__(name, queue, knowledge_base)
        self.agent_registry = agent_registry
        agent_registry.register("installment_plan", queue)
        self.task = "Your task is to evaluate debtor information and create an installment plan by reasoning based on the provided business rules."

    async def process_message(self, entity: DebtorProfile):
        try:
            logging.info(f"{self.name} received message: {entity}")
            business_rules = await self.retrieve()
            content = f"debtor profile: {entity}, business rules: {business_rules}"

            reasoning_task = asyncio.create_task(
                self.reason_structured(
                    content=content, response_format=InstallmentPlan, task=self.task
                )
            )

            result = await reasoning_task

            logging.info(
                f"{self.name} created installment plan for {entity.name}: {result}"
            )

            target_queues = self.agent_registry.get_agents_for_task("contact_debtor")
            asyncio.create_task(self.publish_message(target_queues, entity))

        except Exception as e:
            logging.error(f"{self.name} encountered an exception: {e}")

    async def retrieve(self):
        try:
            query = "How to calculate the montly payment for a debtor?"
            logging.debug(f"retrieve {query}")
            rules = await self.query_knowledge(query)
            return rules
        except Exception as e:
            logging.error(f"Error retrieving business rules: {e}")
