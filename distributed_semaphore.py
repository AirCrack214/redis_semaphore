from redis import Redis
from time import time

class DistributedSemaphore():

    def __init__(self, bounded_limit):
        self.client = Redis()
        if bounded_limit < 1:
            raise ValueError("Bounded limit must be positive")
        self.bounded_limit = bounded_limit
        self.operations = list()

    def _exists_or_init(self):
        old_key = self.status(self.check_exists_key)
        if old_key:
            return False
        return self._init()

    def _init(self):
        self.client.expire(self.check_exists_key, 10)
        with self.client.pipeline() as pipe:
            pipe.multi()
            pipe.delete(self.grabbed_key, self.available_key)
            pipe.rpush(self.available_key, *range(self.bounded_limit))
            pipe.execute()
        self.client.persist(self.check_exists_key)

    def status(self, method : str):
        return self.client.getset(method, 'ok')

    def acquire(self):
        self._exists_or_init()

        pair = self.client.blpop(self.available_key, 0)
        if pair is None:
            raise ValueError("Unable to acquire semaphore due to bounded limit")
        token = pair[1]

        self.operations.append(token)
        self.client.hset(self.grabbed_key, token, time())
        return token

    def release_stale_locks(self, expires=10):
        token = self.status(self.check_release_locks_key)
        if token:
            return False
        self.client.expire(self.check_release_locks_key, expires)
        try:
            for token, looked_at in self.client.hgetall(self.grabbed_key).items():
                if float(looked_at) < time():
                    self.signal(token)
        finally:
            self.client.delete(self.check_release_locks_key)

    def _is_locked(self, token):
        return self.client.hexists(self.grabbed_key, token)

    def has_lock(self):
        for t in self.operations:
            if self._is_locked(t):
                return True
        return False

    def release(self):
        if not self.has_lock():
            return False
        return self.signal(self.operations.pop())

    def reset(self):
        self._init()

    def signal(self, token):
        if token is None:
            return None
        with self.client.pipeline() as pipe:
            pipe.multi()
            pipe.hdel(self.grabbed_key, token)
            pipe.lpush(self.available_key, token)
            pipe.execute()
            return token
    
    @property
    def available_bounded_limit(self):
        return self.client.llen(self.available_key)
    @property
    def check_exists_key(self):
        return self.get_key('EXISTS')
    @property
    def available_key(self):
        return self.get_key('AVAILABLE')
    @property
    def grabbed_key(self):
        return self.get_key('GRABBED')
    @property
    def check_release_locks_key(self):
        return self.get_key('RELEASE_LOCKS')

    def get_key(self, suffix):
        return f'SEMAPHORE:{suffix}'

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        return True if exc_type is None else False