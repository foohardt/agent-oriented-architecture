import logging
from asyncio import Queue

from config import openai_client
from .base import CognitiveAgent
from knowledge import KnowledgeBase
from .registry import AgentRegistry
from models import DebtorProfile, NextBestAction


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

    async def process_message(self, entity: DebtorProfile):
        logging.info(f"{self.name} received profile: {entity}")
        rules = await self.retrieve(entity)
        
        next_action = await self.reason(entity, rules)
        logging.info(f"{self.name} decided next action: {next_action}")
        
        target_queues = self.agent_registry.get_agents_for_task(next_action.action)
        await self.publish_message(target_queues, entity)


    async def retrieve(self, entity: DebtorProfile):
        try:
            query = f"Risk level is {entity.risk_level} and overdue days is {
                entity.overdue_days}."
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
                        "content": "You are a debt collection assistant. Your task is to evaluate debtor information and determine the next best action by reasoning based on the provided business rules.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=NextBestAction,
            )

            next_action = completion.choices[0].message.parsed

            return next_action
        except Exception as e:
            raise RuntimeError(f"Failed to generate decision: {e}")

    async def delegate_task(self, action: NextBestAction, entity: DebtorProfile):
        target_queues = self.agent_registry.get_agents_for_task(action.action)
        if not target_queues:
            logging.info(
                f"{self.name}: No agents available for task '{action}'.")
            return
        for queue in target_queues:
            await queue.put(entity)
            logging.info(f"{self.name} delegated profile to queue.")
