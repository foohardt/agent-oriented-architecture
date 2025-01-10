import logging

from .base import CognitiveAgent


class InstallmentPlanAgent(CognitiveAgent):
    def __init__(self, name, input_queue, knowledge_base, agent_registry):
        super().__init__(name, input_queue, knowledge_base)
        agent_registry.register("payment_plan", input_queue)

    async def process_message(self, profile):
        logging.info(f"{self.name} is generating a payment plan for profile: {profile}")
