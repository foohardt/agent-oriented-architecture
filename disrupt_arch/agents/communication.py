from asyncio import Queue

from knowledge import KnowledgeBase

from .base import CognitiveAgent
from .registry import AgentRegistry


class CommunicationAgent(CognitiveAgent):
    def __init__(
        self,
        name: str,
        queue: Queue,
        knowledge_base: KnowledgeBase,
        agent_registry: AgentRegistry,
    ):
        super().__init__(name, queue, knowledge_base)
        self.agent_registry = agent_registry
        self.agent_registry.register("communicate_debtor", queue)

    async def process_message(self):
        return NotImplementedError

    async def reason(self):
        return NotImplementedError
