import redis.asyncio as redis
import json
from .config import settings

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        return self.redis

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        return await self.redis.set(key, value, ex=ex)

    async def set_json(self, key: str, value: dict, ex: int = None):
        """Set a JSON object in Redis"""
        return await self.redis.set(key, json.dumps(value), ex=ex)

    async def get_json(self, key: str):
        """Get a JSON object from Redis"""
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def delete(self, key: str):
        return await self.redis.delete(key)

    async def publish(self, channel: str, message: str):
        return await self.redis.publish(channel, message)

    async def subscribe(self, channel: str):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

redis_client = RedisClient()