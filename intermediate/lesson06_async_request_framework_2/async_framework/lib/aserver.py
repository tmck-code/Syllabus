import asyncio
from dataclasses import dataclass
import functools
import json
import random
import time

from aiohttp import web
from faker import Faker

class APIError(Exception):
    def __init__(self, *args, info: dict = {}, **kwargs):
        self.info = info
        super().__init__(*args, **kwargs)

class RateLimitError(APIError): pass

@dataclass
class Rater:
    max_requests: int
    time_window: int = 60

    def __post_init__(self):
        self.start_time = time.time()
        self.total = 0

    def __time_remaining(self):
        return self.time_window-(time.time()-self.start_time)

    def inc(self):
        # If we are over the time window, reset counter & time
        if (time.time() - self.start_time) > self.time_window:
            self.total = 0
            self.start_time = time.time()
        # Now, increment the total
        self.total += 1
        # If there are too many requests, raise error
        if self.total > self.max_requests:
            raise RateLimitError(
                "Exceeded rate limit",
                info={
                    "limit": self.max_requests,
                    "current": self.total,
                    "remaining": self.__time_remaining()
                }
            )
        self.__random_errorz()

    def __random_errorz(self):
        if random.randint(0, 100) % 49 == 0:
            raise APIError()


def with_rater(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        args[0].total += 1
        print(f"Request {args[0].total} to '{func.__name__}': {args[1]}")
        try:
            args[0].rate_limit.inc()
        except RateLimitError as e:
            print(f"Rate limiting!", e.info)
            return web.Response(text=json.dumps({"error": e.info}), status=429)
        except APIError as e:
            print(f"API Error!", e.info)
            return web.Response(text=json.dumps({"error": e.info}), status=503)

        await asyncio.sleep(random.uniform(1, 3))

        return await func(*args, **kwargs)
    return wrapped


@dataclass
class API:
    rate_limit: Rater
    max_items: int = 100

    def __post_init__(self):
        self.last_request = time.time()
        self.faker = Faker()
        self.total = 0
        self.items = [self.faker.email() for _ in range(self.max_items)]

    @with_rater
    async def get_root(self, request):
        return web.Response(text="Hello, world\n")

    @with_rater
    async def get_items(self, request):
        return web.Response(text=json.dumps(list(range(self.max_items))))

    @with_rater
    async def get_item(self, request):
        idx = int(request.match_info["id"])
        return web.Response(text=json.dumps({"email": self.items[idx]}))

    def routes(self):
        return [
            web.get('/',           self.get_root),
            web.get('/items',      self.get_items),
            web.get('/items/{id}', self.get_item),
        ]


@dataclass
class AServer:
    rate_limit: Rater
    max_items: int

    def run(self):
        api = API(rate_limit=self.rate_limit, max_items=self.max_items)
        app = web.Application()
        app.add_routes(api.routes())
        web.run_app(app)
