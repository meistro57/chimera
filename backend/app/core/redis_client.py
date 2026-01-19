import json
import logging
import redis.asyncio as redis

from .config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.redis = None
        self._fallback_store = {}

    async def connect(self):
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        except Exception as exc:
            logger.warning("Redis connection unavailable, using in-memory fallback: %s", exc)
        return self.redis

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def get(self, key: str):
        if self.redis:
            try:
                return await self.redis.get(key)
            except Exception as exc:
                logger.warning("Redis get failed, falling back: %s", exc)
                self.redis = None
        return self._fallback_store.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        if self.redis:
            try:
                return await self.redis.set(key, value, ex=ex)
            except Exception as exc:
                logger.warning("Redis set failed, falling back: %s", exc)
                self.redis = None
        self._fallback_store[key] = value
        return True

    async def set_json(self, key: str, value: dict, ex: int = None):
        return await self.set(key, json.dumps(value), ex=ex)

    async def get_json(self, key: str):
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception as exc:
            logger.warning("Failed to decode JSON value for key %s: %s", key, exc)
            return None

    async def delete(self, key: str):
        if self.redis:
            try:
                return await self.redis.delete(key)
            except Exception as exc:
                logger.warning("Redis delete failed, falling back: %s", exc)
                self.redis = None
        return self._fallback_store.pop(key, None) is not None

    async def publish(self, channel: str, message: str):
        if self.redis:
            try:
                return await self.redis.publish(channel, message)
            except Exception as exc:
                logger.warning("Redis publish failed, falling back: %s", exc)
                self.redis = None
        logger.debug("Redis publish skipped; channel=%s", channel)
        return 0

    async def subscribe(self, channel: str):
        if not self.redis:
            logger.warning("Redis subscribe unavailable; falling back to noop for channel %s", channel)
            return None
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


redis_client = RedisClient()
