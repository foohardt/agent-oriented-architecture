from abc import abstractmethod
from asyncio import Queue

from knowledge import KnowledgeBase

from .agent import Agent


class CognitiveAgent(Agent):
    def __init__(self, name: str, input_queue: Queue, knowledge_base: KnowledgeBase):
        """
        Base class for agents that use the knowledge base.
        :param name: The name of the agent.
        :param input_queue: The asyncio queue for receiving messages.
        :param knowledge_base: The KnowledgeBase instance for reasoning.
        """
        super().__init__(name, input_queue)
        self.knowledge_base = knowledge_base

    async def query_knowledge(self, query):
        """Queries the knowledge base."""
        return self.knowledge_base.query_knowledge(query)

    @abstractmethod
    async def process_message(self, message):
        pass
