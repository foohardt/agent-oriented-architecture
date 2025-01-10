import logging
from asyncio import Queue

from knowledge import KnowledgeBase

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

    async def process_message(self, profile):
        logging.info(f"{self.name} received profile: {profile}")
        rules = await self.query_knowledge("task rules")
        next_action = await self.decide_next_action(profile, rules)
        logging.info(f"{self.name} decided next action: {next_action}")
        await self.delegate_task(next_action, profile)

    async def decide_next_action(self, profile, rules):
        if profile.get("risk_level") == "high" and profile.get(
            "overdue_days", 0
        ) > rules.get("escalation_threshold", 90):
            return "escalate"
        elif profile.get("outstanding_balance", 0) > 1000:
            return "payment_plan"
        return "monitor"

    async def delegate_task(self, action, profile):
        target_queues = self.agent_registry.get_agents_for_task(action)
        if not target_queues:
            logging.info(f"{self.name}: No agents available for task '{action}'.")
            return
        for queue in target_queues:
            await queue.put(profile)
            logging.info(f"{self.name} delegated profile to queue.")
