import asyncio
import logging
import time
from unittest import IsolatedAsyncioTestCase

from agents import AgentRegistry, RiskAssessmentAgent, TaskAgent
from chromadb.utils import embedding_functions
from config import chroma_client
from knowledge import KnowledgeBase
from models import DebtorProfile
from samples import generate_samples


class TestConcurrentWorkflows(IsolatedAsyncioTestCase):
    async def test_concurrent_workflows(self):
        logging.basicConfig(level=logging.INFO)

        task_queue = asyncio.Queue()
        risk_queue = asyncio.Queue()
        active_tasks = 0

        agent_registry = AgentRegistry()
        agent_registry.register("assess_risk", risk_queue)

        task_agent = TaskAgent(
            "TaskAgent",
            task_queue,
            KnowledgeBase(
                chroma_client.get_collection(
                    "business_rules",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
                )
            ),
            agent_registry,
        )
        risk_agent = RiskAssessmentAgent(
            "RiskAssessmentAgent", risk_queue, agent_registry
        )

        samples = generate_samples(2)

        task_start_times = {}
        task_end_times = {}

        async def track_task_execution(sample: DebtorProfile):
            """Helper function to track task start & end times"""
            nonlocal active_tasks
            task_name = sample.name

            start_time = time.time()
            task_start_times[task_name] = start_time
            active_tasks += 1
            logging.info(
                f"🔹 Task {task_name} started at {start_time}, Active Tasks: {active_tasks}"
            )

            await task_queue.put(sample)

            # Simulate processing delay (avoid fixed sleep)
            await asyncio.sleep(0.1)

            end_time = time.time()
            task_end_times[task_name] = end_time
            active_tasks -= 1
            logging.info(
                f"Task {task_name} finished at {end_time}, Active Tasks: {active_tasks}"
            )

        agents = [
            asyncio.create_task(task_agent.run()),
            asyncio.create_task(risk_agent.run()),
        ]

        # Put tasks in queue and track execution
        task_tracking = [
            asyncio.create_task(track_task_execution(sample)) for sample in samples
        ]
        await asyncio.gather(*task_tracking)

        await asyncio.sleep(1)

        assert task_queue.empty(), "Task queue should be empty after processing"
        assert risk_queue.empty(), "Risk queue should be empty after processing"

        #  erify concurrency (Tasks should have overlapped)
        concurrent_tasks = any(
            task_start_times[sample1] < task_end_times[sample2]
            and task_start_times[sample2] < task_end_times[sample1]
            for sample1 in task_start_times
            for sample2 in task_start_times
            if sample1 != sample2
        )

        assert concurrent_tasks, "Tasks did not execute in parallel."

        for agent in agents:
            agent.cancel()
        await asyncio.gather(*agents, return_exceptions=True)

        logging.info(f"Task Start Times: {task_start_times}")
        logging.info(f"Task End Times: {task_end_times}")
