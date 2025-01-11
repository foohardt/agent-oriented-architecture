import logging
from asyncio import Queue

from .base import OperationalAgent
from .registry import AgentRegistry


class EscalationAgent(OperationalAgent):
    def __init__(self, name: str, queue: Queue, agent_registry: AgentRegistry):
        super().__init__(name, queue)
        agent_registry.register("escalate", queue)

    async def process_message(self, profile):
        logging.info(f"{self.name} is escalating profile: {profile}")

    async def execute_task(self, task):
        logging.info(f"{self.name}: Executing escalation task {task}")
