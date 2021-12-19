from collections import Counter
from dataclasses import field, dataclass
from abc import ABC, abstractmethod
from typing import List
import time

from aiohttp import ClientResponseError, request
import asyncio


class Sentinel: pass

class ThrottledQueue(asyncio.Queue):
    "subclass asyncio.Queue i.e. import all behaviour"

    def __init__(self, per_second, debug=False, maxsize=0, *, loop=None, i=0):
        "Set up some extra vars and then call the original init"

        self.lock = asyncio.Lock()
        self.i = i
        self.per_second = per_second
        self.last_get = time.time() # this is the fastest way... I think?
        self.debug = debug
        super(ThrottledQueue, self).__init__(maxsize=maxsize, loop=loop)

    async def notify(self, override: int=0):
        """
        Signals to the queue that an item is being retried,
        so pause any get()s by aquiring the lock and throttling before releasing
        """
        async with self.lock:
            await self._throttle(override)

    async def get(self):
        async with self.lock:
            await self._throttle()
            result = await super(ThrottledQueue, self).get()

            self.last_get = time.time()
            return result

    async def _throttle(self, override: int=0):
        if override > 0:
            print(f"Throttling for override: {override}")
            await asyncio.sleep(override)
            return
        elapsed = time.time() - self.last_get
        sleep_time = (1/float(self.per_second)) - elapsed
        if self.debug:
            print(self.i, '- times', f'{elapsed:.5f}', '+', f'{sleep_time:.5f}', '=', self.per_second, '- sizes', self.qsize(), f'{self.qsize() / max(1, self.maxsize):.5f}')
        await asyncio.sleep(max(0, sleep_time)) # Make sure we wait at least 0 seconds

@dataclass
class AsyncEndpoint(ABC):

    per_second: int

    def create_queue(self):
        return ThrottledQueue(per_second=10, debug=True)

    @abstractmethod
    async def response_unpacker(self, req_data, resp, queue, *args):
        "Unpacks the response into individual items to put on a queue"

    @abstractmethod
    def request_builder(self, method, hostname, port, endpoint, payload=None):
        "Builds the *args and **kwargs to be passed to aiohttp.request()"

    @abstractmethod
    async def error_handler(self, e, q):
        "Handles API errors"

from dataclasses import field

@dataclass
class AsyncEndpointPipeline:
    endpoints: List[AsyncEndpoint]
    initial: List[tuple]

    async def async_run_pipeline(self):
        pipeline = []
        in_q, out_q = None, None
        results = asyncio.Queue()

        for i, e in enumerate(self.endpoints):
            if i == 0:
                in_q = await _fill_queue(ThrottledQueue(per_second=e.per_second), self.initial)
            if i == len(self.endpoints)-1:
                out_q = results
            else:
                out_q = ThrottledQueue(per_second=self.endpoints[i+1].per_second)
            a = AsyncRequester(
                in_q=in_q,
                out_q=out_q,
                req_builder=e.request_builder,
                resp_unpacker=e.response_unpacker,
                error_handler=e.error_handler,
            ).consumer(i)
            pipeline.append(a)
            in_q = out_q

        await asyncio.gather(
            *pipeline
        )
        return results
    
    def run_pipeline(self):
        return asyncio.run(self.async_run_pipeline())

@dataclass
class AsyncRequester:
    in_q: ThrottledQueue
    out_q: ThrottledQueue
    req_builder: object
    resp_unpacker: object
    error_handler: object
    log_prefix: str = "---"
    cntr: Counter = field(default_factory=Counter)

    async def consumer(self, idx):
        print(f"Starting worker {idx}")
        retrying = False
        while True:
            if not retrying:
                d = await self.in_q.get()
                print(self.log_prefix, d)
                if d == Sentinel:
                    await self.in_q.put(Sentinel)
                    await self.out_q.put(Sentinel)
                    print(self.log_prefix, f"worker {idx} exiting")
                    return
            retrying = False
            print("++++", self.req_builder, d)
            async with request(*self.req_builder(*d)) as req:
                resp = await req.read()
                try:
                    req.raise_for_status()
                except ClientResponseError as e:
                    self.cntr["failure"] += 1
                    await self.error_handler(e, self.in_q)
                    retrying = True
                    # TODO implement retry limit
                    continue
                print(self.log_prefix, f"worker {idx} response: {resp}")
                print(self.log_prefix, f"sending to queue: {resp}")
                await self.resp_unpacker(d, resp, self.out_q)
                self.cntr["success"] += 1


async def _fill_queue(q, items):
    for idx, i in enumerate(items):
        await q.put(i)
    await q.put(Sentinel)
    return q

async def _unpack_queue(q):
    l = list()
    for idx in range(q.qsize()):
        l.append(await q.get())
    return l

def unpack_queue(q):
    return asyncio.run(_unpack_queue(q))

