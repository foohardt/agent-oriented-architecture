import logging
from abc import abstractmethod
from asyncio import Queue
from typing import Type

from config import openai_client
from knowledge import KnowledgeBase
from pydantic import BaseModel

from .agent import Agent


class CognitiveAgent(Agent):
    def __init__(self, name: str, input_queue: Queue, knowledge_base: KnowledgeBase):
        """
        Base class for agents that use reasoning capabilities.
        :param name: The name of the agent.
        :param input_queue: The asyncio queue for receiving messages.
        :param knowledge_base: The KnowledgeBase instance for reasoning.
        """
        super().__init__(name, input_queue)
        self.knowledge_base = knowledge_base

    @abstractmethod
    async def process_message(self, message):
        pass

    async def reason_structured(
        self, content: str, response_format: Type[BaseModel], task: str
    ):
        try:
            completion = openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a debt collection assistant. {task}",
                    },
                    {"role": "user", "content": content},
                ],
                response_format=response_format,
            )

            result = completion.choices[0].message.parsed

            return result
        except Exception as e:
            logging.error(f"{self.name} encountered an error reasoning: {e}")

    async def reason_unstructured(self, content: str, task: str):
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "developer",
                        "content": f"You are a debt collection assistant. {task}",
                    },
                    {"role": "user", "content": content},
                ],
            )

            resukt = completion.choices[0].message

            return resukt
        except Exception as e:
            logging.error(f"{self.name} encountered an error reasoning: {e}")

    async def query_knowledge(self, query):
        """Queries the knowledge base."""
        return self.knowledge_base.query_knowledge(query)
