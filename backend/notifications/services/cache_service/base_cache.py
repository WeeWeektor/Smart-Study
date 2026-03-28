import asyncio
import logging

from common.services import register_cache_key


class BaseCache:
    logger = logging.getLogger(__name__)
    _background_tasks = set()
    CACHE_NAME = "calendar_events"
    CACHE_VERSION = 1

    def __init__(self, key):
        self.key = key

    async def register_key(self):
        task = asyncio.create_task(self._do_register())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _do_register(self):
        try:
            await register_cache_key(self.key, self.CACHE_NAME)
        except Exception as e:
            self.logger.error(f"Failed to register cache key {self.key}: {e}")
