import asyncio


class MessageBroker:
    def __init__(self):
        self.queues = {}

    def get_queue(self, name):
        if name not in self.queues:
            self.queues[name] = asyncio.Queue()
        return self.queues[name]

    async def publish(self, queue_name, message):
        queue = self.get_queue(queue_name)
        await queue.put(message)
