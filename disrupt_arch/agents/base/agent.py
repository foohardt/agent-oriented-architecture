from abc import ABC, abstractmethod
import logging

from asyncio import CancelledError, Queue


class Agent(ABC):
    def __init__(self, name: str, queue: Queue):
        """
        Base class for all agents.
        :param name: The name of the agent.
        :param queue: The asyncio queue for receiving messages.
        """
        self.name = name
        self.queue = queue

    async def run(self):
        """Starts the event loop for the agent."""
        try:
            while True:
                profile = await self.queue.get()
                await self.process_message(profile)
        except CancelledError:
            logging.info(f"{self.name} is shutting down. All tasks processed.")

    @abstractmethod
    async def process_message(self, profile):
        """Processes an incoming message."""
        pass
