import logging

from config import openai_client
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

    async def process_message(self, entity: DebtorProfile):
        logging.info(f"{self.name} received profile: {entity}")
        rules = await self.retrieve()
        logging.debug(rules)
        result = await self.reason(entity, rules)
        logging.info(
            f"{self.name} created installment plan for {entity.name}: {
                result.get('installment_plan')
            }"
        )

        target_queues = self.agent_registry.get_agents_for_task(result.get("action"))
        await self.publish_message(target_queues, entity)

    async def retrieve(self):
        try:
            query = "How to calculate the montly payment for a debtor?"
            logging.debug(f"retrieve {query}")
            rules = await self.query_knowledge(query)
            return rules
        except Exception as e:
            logging.error(f"Error retrieving business rules: {e}")

    async def reason(self, entity: DebtorProfile, rules):
        prompt = f"""
        debtor profile: {entity},
        rules: {rules}
        """
        try:
            completion = openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a debt collection assistant. Your task is to evaluate debtor information and create an installment plan by reasoning based on the provided business rules.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=InstallmentPlan,
            )

            installment_plan = completion.choices[0].message.parsed

            return {
                "action": "communicate_debtor",
                "installment_plan": installment_plan,
            }
        except Exception as e:
            logging.error(f"Error reasoning next best action: {e}")
