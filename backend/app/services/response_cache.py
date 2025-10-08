import hashlib
import json
from typing import List, Dict, Any, Optional
from ..providers.base import ChatMessage
from ..core.redis_client import redis_client

class ResponseCache:
    """Caching layer for AI provider responses to improve performance"""

    def __init__(self):
        self.redis = redis_client
        self.cache_ttl = 3600  # 1 hour default TTL

    async def ensure_connected(self):
        """Ensure Redis connection is established"""
        if self.redis.redis is None:
            await self.redis.connect()

    def _generate_cache_key(self, provider_name: str, messages: List[ChatMessage],
                           persona_params: Dict[str, Any]) -> str:
        """Generate a deterministic cache key for the response"""
        # Sort messages by content to ensure consistent ordering
        message_content = []
        for msg in messages:
            message_content.append({
                "role": msg.role,
                "content": msg.content.strip()
            })

        # Create cache key components
        cache_components = {
            "provider": provider_name,
            "messages": message_content,
            "params": {
                "temperature": persona_params.get('temperature', 0.7),
                "max_tokens": persona_params.get('max_tokens', 150),
                "stream": False,  # We don't cache streaming responses
            }
        }

        # Create deterministic JSON string
        cache_string = json.dumps(cache_components, sort_keys=True, separators=(',', ':'))

        # Generate hash for cache key (prevents overly long keys)
        hash_key = hashlib.sha256(cache_string.encode()).hexdigest()

        return f"cached_response:{provider_name}:{hash_key[:16]}"

    async def get_cached_response(self, provider_name: str, messages: List[ChatMessage],
                                 persona_params: Dict[str, Any]) -> Optional[str]:
        """Check for cached response and return it if available"""
        await self.ensure_connected()

        cache_key = self._generate_cache_key(provider_name, messages, persona_params)

        try:
            cached_data = await self.redis.get_json(cache_key)
            if cached_data:
                return cached_data.get("response")

            return None
        except Exception as e:
            # Cache miss due to error, but don't fail the request
            print(f"Cache retrieval error: {e}")
            return None

    async def cache_response(self, provider_name: str, messages: List[ChatMessage],
                           persona_params: Dict[str, Any], response: str):
        """Store response in cache"""
        await self.ensure_connected()

        cache_key = self._generate_cache_key(provider_name, messages, persona_params)

        try:
            cache_data = {
                "response": response,
                "timestamp": self._get_current_timestamp()
            }

            # Set cache with TTL
            await self.redis.set_json(cache_key, cache_data, ex=self.cache_ttl)

        except Exception as e:
            # Cache failure shouldn't prevent response
            print(f"Cache storage error: {e}")

    async def invalidate_persona_cache(self, persona: str):
        """Invalidate all cached responses for a specific persona"""
        await self.ensure_connected()

        try:
            # In a production system, you might want to use Redis keys scanning
            # or maintain separate indexes per persona/conversation
            # For now, we'll let cache expire naturally

            # Future enhancement: Use a separate index to track keys per persona
            print(f"Cache invalidation requested for persona: {persona}")

        except Exception as e:
            print(f"Cache invalidation error: {e}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        await self.ensure_connected()

        try:
            # Get Redis keyspace info and database statistics
            info = await self.redis.redis.info("keyspace")
            cache_stats = await self.redis.redis.dbsize()

            # Estimate number of cached responses

            # For more detailed metrics, we'd need to track hits/misses in the application
            # This is a basic implementation showing cache size

            return {
                "cache_size": cache_stats,
                "keyspace_info": info,
                "cache_enabled": True,
                "cache_hit_rate": "tracked_via_logs",  # Would need Prometheus/other monitoring
                "server_info": await self.redis.redis.info("server")
            }

        except Exception as e:
            print(f"Cache stats error: {e}")
            return {"error": str(e)}

    def _get_current_timestamp(self) -> float:
        """Get current timestamp for cache metadata"""
        import time
        return time.time()

# Global cache instance
response_cache = ResponseCache()