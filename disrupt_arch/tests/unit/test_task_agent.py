import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from agents import TaskAgent
from models import DebtorProfile, NextBestAction


class TestTaskAgent(unittest.IsolatedAsyncioTestCase):
    async def test_process_message(self):
        mock_registry = MagicMock()
        mock_registry.get_agents_for_task.return_value = [asyncio.Queue()]
        mock_knowledge_base = AsyncMock()
        mock_knowledge_base.query_knowledge.return_value = "Rule 1, Rule 2"
        mock_openai_client = MagicMock()
        mock_openai_client.beta.chat.completions.parse.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        parsed=NextBestAction(
                            action="escalate", target="EscalationAgent"
                        )
                    )
                )
            ]
        )

        task_queue = asyncio.Queue()
        agent = TaskAgent(
            "TaskAgent",
            task_queue,
            mock_knowledge_base,
            mock_registry,
        )

        profile = DebtorProfile(
            communication_state="NO_RESPONSE",
            name="John Doe",
            income=50000.0,
            installment_plan=None,
            outstanding_balance=2000.0,
            overdue_days=120,
            risk_level=None,
        )
        await task_queue.put(profile)

        agent.retrieve = AsyncMock(return_value="Rule 1, Rule 2")
        agent.reason_structured = AsyncMock(
            return_value=NextBestAction(action="escalate", target="EscalationAgent")
        )

        task = asyncio.create_task(agent.run())
        await asyncio.sleep(0.1)
        task.cancel()

        agent.retrieve.assert_awaited_once_with(profile)
        agent.reason_structured.assert_awaited_once_with(
            content=f"debtor profile: {profile}, business rules: Rule 1, Rule 2",
            response_format=NextBestAction,
            task=agent.task,
        )
        mock_registry.get_agents_for_task.assert_called_with("escalate")
