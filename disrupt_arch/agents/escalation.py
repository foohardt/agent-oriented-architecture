import logging

from .base import OperationalAgent


class EscalationAgent(OperationalAgent):
    def __init__(self, name, input_queue, agent_registry):
        super().__init__(name, input_queue)
        agent_registry.register("escalate", input_queue)

    async def process_message(self, profile):
        logging.info(f"{self.name} is escalating profile: {profile}")

    async def execute_task(self, task):
        logging.info(f"{self.name}: Executing escalation task {task}")
