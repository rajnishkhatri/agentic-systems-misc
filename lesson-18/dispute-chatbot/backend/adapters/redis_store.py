"""Redis Persistence Adapter (Task 7.9).

Implements async Redis client wrapper for state saving/loading.
"""

import json
import logging
import os
from typing import Any

import redis.asyncio as redis


class RedisStore:
    """Async Redis adapter for state persistence."""

    def __init__(self, redis_url: str | None = None) -> None:
        """Initialize Redis store.

        Args:
            redis_url: Redis connection string (defaults to env var REDIS_URL or localhost)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client: redis.Redis | None = None
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> None:
        """Connect to Redis."""
        if not self.client:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            try:
                await self.client.ping()
                self.logger.info("Connected to Redis at %s", self.redis_url)
            except Exception as e:
                self.logger.warning("Failed to connect to Redis: %s. Continuing without Redis persistence.", e)
                # Close the client to prevent further errors
                await self.client.close()
                self.client = None
                # Do NOT raise, allowing soft fallback

    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None

    async def save_state(self, task_id: str, state: dict[str, Any], ttl: int = 86400) -> None:
        """Save workflow state to Redis.

        Args:
            task_id: Unique task identifier
            state: State dictionary to save
            ttl: Time to live in seconds (default 24h)
        """
        if not self.client:
            # Try to connect, but if it fails (client is None), just return
            await self.connect()

        if self.client:
            key = f"dispute:state:{task_id}"
            await self.client.set(key, json.dumps(state), ex=ttl)

    async def load_state(self, task_id: str) -> dict[str, Any] | None:
        """Load workflow state from Redis.

        Args:
            task_id: Unique task identifier

        Returns:
            State dictionary or None if not found
        """
        if not self.client:
            await self.connect()

        if self.client:
            key = f"dispute:state:{task_id}"
            data = await self.client.get(key)
            if data:
                return json.loads(data)

        return None

