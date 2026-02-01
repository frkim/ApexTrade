"""Event bus for pub/sub messaging."""

import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class EventBus:
    """Event bus for publishing and subscribing to events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}
        self._local_mode = False

    async def publish(self, event_type: str, data: dict[str, Any]) -> None:
        """Publish an event to all subscribers."""
        message = json.dumps({
            "type": event_type,
            "data": data,
        })

        if self._local_mode:
            await self._dispatch_local(event_type, data)
        else:
            try:
                await redis_client.publish(f"events:{event_type}", message)
                logger.debug(f"Published event: {event_type}")
            except Exception as e:
                logger.error(f"Failed to publish event: {e}")
                await self._dispatch_local(event_type, data)

    async def _dispatch_local(self, event_type: str, data: dict[str, Any]) -> None:
        """Dispatch event to local handlers."""
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type with a handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            logger.debug(f"Unsubscribed from event: {event_type}")

    async def start_listening(self, *event_types: str) -> None:
        """Start listening for events from Redis."""
        try:
            pubsub = await redis_client.subscribe(
                *[f"events:{et}" for et in event_types]
            )

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        event_type = data.get("type")
                        event_data = data.get("data", {})
                        await self._dispatch_local(event_type, event_data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in event: {message['data']}")
        except Exception as e:
            logger.error(f"Error listening for events: {e}")

    def set_local_mode(self, enabled: bool = True) -> None:
        """Enable or disable local mode (no Redis)."""
        self._local_mode = enabled


event_bus = EventBus()


class EventTypes:
    """Event type constants."""

    STRATEGY_ACTIVATED = "strategy.activated"
    STRATEGY_DEACTIVATED = "strategy.deactivated"
    STRATEGY_SIGNAL = "strategy.signal"

    TRADE_OPENED = "trade.opened"
    TRADE_CLOSED = "trade.closed"
    TRADE_MODIFIED = "trade.modified"

    BACKTEST_STARTED = "backtest.started"
    BACKTEST_COMPLETED = "backtest.completed"
    BACKTEST_FAILED = "backtest.failed"

    MARKET_DATA_UPDATED = "market_data.updated"

    POSITION_OPENED = "position.opened"
    POSITION_CLOSED = "position.closed"
    POSITION_UPDATED = "position.updated"
