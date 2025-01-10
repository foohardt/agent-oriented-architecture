import logging

from .base import CognitiveAgent
from knowledge import KnowledgeBase
from registry import AgentRegistry


class InstallmentPlanAgent(CognitiveAgent):
    def __init__(self, name, queue, knowledge_base: KnowledgeBase, agent_registry: AgentRegistry):
        super().__init__(name, queue, knowledge_base)
        agent_registry.register("payment_plan", queue)

    async def process_message(self, profile):
        logging.info(f"{self.name} is generating a payment plan for profile: {profile}")
