from abc import abstractmethod

from .agent import Agent


class OperationalAgent(Agent):
    @abstractmethod
    async def execute_task(self, task):
        """Executes a predefined task."""
        pass
