import asyncio
import pytest
import time
import csv
import os
import matplotlib.pyplot as plt
from unittest.mock import AsyncMock

from agents import (
    AgentRegistry,
    CommunicationAgent,
    InstallmentPlanAgent,
    RiskAssessmentAgent,
    TaskAgent,
)
from chromadb.utils import embedding_functions
from config import chroma_client
from knowledge import KnowledgeBase
from models import InstallmentPlan
from samples import generate_samples


@pytest.mark.asyncio
async def test_multiple_sample_sizes():
    """
    Runs the test with multiple sample sizes and stores results.
    """
    sample_sizes = [5, 10, 25, 50, 100]  
    output_dir = "disrupt_arch/tests/metrics/results"
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, "test_results.csv")

    csv_headers = ["Run", "Num Samples", "Execution Time", "Throughput", "Communication Overhead", "Average Latency", "Task Balance"]
    if not os.path.exists(csv_file):
        with open(csv_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(csv_headers)

    metric_logs = []
    
    for num_samples in sample_sizes:
        metric_log = await run_performance_test(num_samples, csv_file)
        metric_logs.append(metric_log)

    plot_metrics(metric_logs, output_dir)


async def run_performance_test(num_samples, csv_file):
    """
    Runs a single test iteration with the given sample size.
    """
    agent_registry = AgentRegistry()
    task_queue = asyncio.Queue()
    risk_queue = asyncio.Queue()
    installment_plan_queue = asyncio.Queue()
    communication_queue = asyncio.Queue()

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
    risk_assessment_agent = RiskAssessmentAgent("RiskAssessmentAgent", risk_queue, agent_registry)
    installment_agent = InstallmentPlanAgent(
        "InstallmentPlanAgent",
        installment_plan_queue,
        KnowledgeBase(
            chroma_client.get_collection(
                "business_rules",
                embedding_function=embedding_functions.DefaultEmbeddingFunction(),
            )
        ),
        agent_registry,
    )
    installment_agent.reason_structured = AsyncMock(
        return_value={
            "action": "contact_debtor",
            "installment_plan": InstallmentPlan(monthly_payment=50, duration_months=12),
        }
    )

    communication_agent = CommunicationAgent(
        "CommunicationAgent",
        communication_queue,
        KnowledgeBase(
            chroma_client.get_collection(
                "business_rules",
                embedding_function=embedding_functions.DefaultEmbeddingFunction(),
            )
        ),
        agent_registry,
    )
    communication_agent.reason_unstructured = AsyncMock(
        return_value="This is a mocked debtor contact message."
    )

    test_profiles = generate_samples(num_samples=num_samples)

    start_time = time.time()
    messages_sent = 0
    task_count = 0
    decision_timestamps = {}
    execution_timestamps = {}

    agent_tasks = [
        asyncio.create_task(task_agent.run()),
        asyncio.create_task(risk_assessment_agent.run()),
        asyncio.create_task(installment_agent.run()),
        asyncio.create_task(communication_agent.run()),
    ]

    for profile in test_profiles:
        await task_queue.put(profile)
        task_count += 1
        decision_timestamps[profile.name] = time.time()

    await asyncio.sleep(5)

    for profile in test_profiles:
        if installment_agent.reason_structured.awaited:
            execution_timestamps[profile.name] = time.time()
            messages_sent += 1

    for task in agent_tasks:
        task.cancel()
    await asyncio.gather(*agent_tasks, return_exceptions=True)

    end_time = time.time()

    execution_time = end_time - start_time
    throughput = task_count / execution_time
    communication_overhead = messages_sent / task_count if task_count else 0
    latencies = [execution_timestamps[name] - decision_timestamps[name] for name in execution_timestamps]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    task_distribution_balance = sum([task_count / len(agent_tasks)]) / len(agent_tasks) if agent_tasks else 0

    metric_log = {
        "run": num_samples,
        "num_samples": num_samples,
        "execution_time": execution_time,
        "throughput": throughput,
        "communication_overhead": communication_overhead,
        "avg_latency": avg_latency,
        "task_distribution_balance": task_distribution_balance
    }

    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(metric_log.values())

    return metric_log


def plot_metrics(metric_logs, output_dir):
    """
    Generates visualizations for collected metrics and overwrites previous images.
    """
    sample_sizes = [m["num_samples"] for m in metric_logs]
    execution_times = [m["execution_time"] for m in metric_logs]
    throughputs = [m["throughput"] for m in metric_logs]
    communication_overheads = [m["communication_overhead"] for m in metric_logs]
    latencies = [m["avg_latency"] for m in metric_logs]
    task_balances = [m["task_distribution_balance"] for m in metric_logs]  # ✅ Now correctly referenced!

    # Execution Time vs Sample Size
    plt.figure(figsize=(10, 5))
    plt.plot(sample_sizes, execution_times, marker='o', linestyle='-', label="Execution Time")
    plt.xlabel("Number of Samples")
    plt.ylabel("Time (seconds)")
    plt.title("Execution Time vs Sample Size")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "execution_time_vs_samples.png"))
    plt.close()

    # Throughput vs Sample Size
    plt.figure(figsize=(10, 5))
    plt.plot(sample_sizes, throughputs, marker='o', linestyle='-', color='r', label="Throughput")
    plt.xlabel("Number of Samples")
    plt.ylabel("Throughput (tasks/sec)")
    plt.title("Throughput vs Sample Size")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "throughput_vs_samples.png"))
    plt.close()

    # Communication Overhead vs Sample Size
    plt.figure(figsize=(10, 5))
    plt.plot(sample_sizes, communication_overheads, marker='o', linestyle='-', color='g', label="Comm Overhead")
    plt.xlabel("Number of Samples")
    plt.ylabel("Messages per Task")
    plt.title("Communication Overhead vs Sample Size")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "communication_overhead_vs_samples.png"))
    plt.close()

    # Latency vs Sample Size
    plt.figure(figsize=(10, 5))
    plt.plot(sample_sizes, latencies, marker='o', linestyle='-', color='purple', label="Avg Latency")
    plt.xlabel("Number of Samples")
    plt.ylabel("Latency (seconds)")
    plt.title("Latency vs Sample Size")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "latency_vs_samples.png"))
    plt.close()

    # Task Distribution Balance vs Sample Size
    plt.figure(figsize=(10, 5))
    plt.plot(sample_sizes, task_balances, marker='o', linestyle='-', color='blue', label="Task Balance")
    plt.xlabel("Number of Samples")
    plt.ylabel("Task Distribution Balance")
    plt.title("Task Distribution Balance vs Sample Size")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "task_balance_vs_samples.png"))
    plt.close()
