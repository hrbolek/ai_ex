import time, asyncio
from typing import Any, Optional


# import json
# import redis.asyncio as redis

# redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# r = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

# # Uložení s TTL (v sekundách)
# await r.setex(f"token:{access_token}", expires_in, json.dumps(token_data))

# # Načtení
# raw = await r.get(f"token:{access_token}")
# token_data = json.loads(raw) if raw else None

# # Smazání
# await r.delete(f"token:{access_token}")

class TokenStore:
    def __init__(self, sweep_interval_sec: int = 60):
        self._data: dict[str, tuple[dict, float]] = {}
        self._sweep_interval = sweep_interval_sec
        self._task: Optional[asyncio.Task] = None

    def set(self, token: str, token_data: dict, ttl_sec: int = 3600) -> None:
        exp = time.time() + max(1, int(ttl_sec))
        self._data[token] = (token_data, exp)

    def get(self, token: str) -> Optional[dict]:
        item = self._data.get(token)
        if not item:
            return None
        data, exp = item
        if time.time() >= exp:
            # expirováno → uklidit a vrátit None
            self._data.pop(token, None)
            return None
        return data

    def delete(self, token: str) -> None:
        self._data.pop(token, None)

    async def _sweeper(self):
        try:
            while True:
                now = time.time()
                expired = [k for k, (_, exp) in self._data.items() if exp <= now]
                for k in expired:
                    self._data.pop(k, None)
                await asyncio.sleep(self._sweep_interval)
        except asyncio.CancelledError:
            pass

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._sweeper())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None