import logging
from asyncio import Queue

from models import DebtorProfile, RiskLevel

from .base import OperationalAgent
from .registry import AgentRegistry


class RiskAssessmentAgent(OperationalAgent):
    def __init__(self, name: str, queue: Queue, agent_registry: AgentRegistry):
        super().__init__(name, queue)
        self.agent_registry = agent_registry
        self.agent_registry.register("assess_risk", queue)

    async def process_message(self, entity: DebtorProfile):
        risk_level = await self.execute_task(entity)
        entity.risk_level = risk_level.value
        logging.info(
            f"{self.name} assessed risk as: {entity.risk_level} for profile: {
                entity.name
            }"
        )
        target_queues = self.agent_registry.get_agents_for_task("next_action")
        await self.publish_message(target_queues, entity)

    async def execute_task(self, entity: DebtorProfile):
        ratio = entity.outstanding_balance / (entity.income or 1)
        if ratio > 0.5 or entity.overdue_days > 120:
            return RiskLevel.HIGH
        elif ratio > 0.2 or entity.overdue_days > 60:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
