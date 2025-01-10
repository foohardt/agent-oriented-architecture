class AgentRegistry:
    def __init__(self):
        self.registry = {}

    def register(self, task, queue):
        """
        Registers a task and its associated queue. Ensures no duplicate registrations.
        :param task: The task type (e.g., "escalate").
        :param queue: The asyncio queue for handling the task.
        """
        if task not in self.registry:
            self.registry[task] = []
        if queue not in self.registry[task]:
            self.registry[task].append(queue)

    def get_agents_for_task(self, task):
        """Retrieves queues capable of handling the task."""
        return self.registry.get(task, [])