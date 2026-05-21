import asyncio
import json
from collections.abc import AsyncIterator


class EventBroker:
    def __init__(self, event_name: str):
        self.event_name = event_name
        self._subscribers: set[asyncio.Queue[str]] = set()

    def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        self._subscribers.discard(queue)

    async def publish(self, payload: dict) -> None:
        if not self._subscribers:
            return

        message = json.dumps(payload, ensure_ascii=False)
        for queue in list(self._subscribers):
            await queue.put(message)

    async def stream(self, queue: asyncio.Queue[str]) -> AsyncIterator[str]:
        try:
            while True:
                message = await queue.get()
                yield f"event: {self.event_name}\ndata: {message}\n\n"
        finally:
            self.unsubscribe(queue)


ingredient_event_broker = EventBroker("ingredient")
liquor_event_broker = EventBroker("liquor")
recommendation_event_broker = EventBroker("recommendation")
sensor_event_broker = EventBroker("sensor")
