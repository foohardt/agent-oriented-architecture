import asyncio
import pytest
from unittest.mock import MagicMock

from agents import TaskAgent


@pytest.mark.asyncio
async def test_agent_concurrent_processing():
    queue = asyncio.Queue()
    agent = TaskAgent(
        "TaskAgent",
        queue,
        MagicMock(),
        MagicMock()
    )

    for i in range(5):
        await queue.put(f"Task-{i}")

    agent_task = asyncio.create_task(agent.run())
    await asyncio.sleep(1)

    assert queue.empty()

    agent_task.cancel()
    await asyncio.gather(agent_task, return_exceptions=True)
