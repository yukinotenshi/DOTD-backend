import redis
import os


class RedisClient:
    def __init__(self):
        self.r = redis.Redis(
            host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=0
        )

    def get(self, key):
        value = self.r.get(key)
        if not value:
            return None
        return value.decode("utf-8")

    def set(self, key, value):
        return self.r.set(key, value)

    def delete(self, key):
        return self.r.delete(key)
