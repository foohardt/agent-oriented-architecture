import asyncio
import logging
from abc import ABC, abstractmethod
from asyncio import Queue

from models import DebtorProfile


class Agent(ABC):
    def __init__(self, name: str, queue: Queue, num_workers: int = 5):
        """
        Base class for all agents.
        :param name: The name of the agent.
        :param queue: The asyncio queue for receiving messages.
        :param num_workers: Number of worker tasks to process messages concurrently.
        """
        self.name = name
        self.queue = queue
        self.num_workers = num_workers
        self.tasks = []

    @abstractmethod
    async def process_message(self, message: DebtorProfile):
        """Process a message received."""
        pass

    async def publish_message(self, queues: list[Queue] | None, entity: DebtorProfile):
        """Publish message in target queues."""
        if not queues:
            logging.warning(
                f"{self.name}: No agents available for target queue.")
            return

        for queue in queues:
            await queue.put(entity)
            logging.info(
                f"{self.name} published profile {entity.name} in queue {queue}.")

    async def worker(self):
        """Worker task that continuously processes messages asynchronously."""
        while True:
            try:
                message = await self.queue.get()
                logging.info(f"{self.name} processing message: {message}")

                await self.process_message(message)

                self.queue.task_done()

            except asyncio.CancelledError as e:
                logging.warning(f"{self.name} worker task cancelled: {e}")
                break
            except Exception as e:
                logging.error(f"{self.name} encountered an error: {e}")

    async def run(self):
        """Starts multiple worker tasks for parallel message processing."""
        logging.info(f"{self.name} starting {self.num_workers} workers...")
        self.tasks = [asyncio.create_task(self.worker())
                      for _ in range(self.num_workers)]

        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError as e:
            logging.warning(
                f"{self.name} CancelledError. Agent shutting down: {e}")
        finally:
            logging.warning(
                f"{self.name} ensuring all tasks complete before shutdown.")
