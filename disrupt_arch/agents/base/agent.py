from abc import ABC, abstractmethod
from asyncio import CancelledError, Queue
import logging

from models import DebtorProfile


class Agent(ABC):
    def __init__(self, name: str, queue: Queue):
        """
        Base class for all agents.
        :param name: The name of the agent.
        :param queue: The asyncio queue for receiving messages.
        """
        self.name = name
        self.queue = queue

    @abstractmethod
    async def process_message(self, profile):
        """Processes an incoming message."""
        pass

    async def publish_message(self, queues: list[Queue] | None, entity: DebtorProfile):
        """Publish message in target queues."""
        if not queues:
            logging.warning(
                f"{self.name}: No agents available for target queue.")
            return

        for queue in queues:
            await queue.put(entity)
            logging.info(f"{self.name} published profile {
                         entity.name} in queue {queue}.")

    async def run(self):
        """Starts the event loop for the agent."""
        try:
            while True:
                profile = await self.queue.get()
                await self.process_message(profile)
        except CancelledError:
            logging.info(f"{self.name} is shutting down. All tasks processed.")
