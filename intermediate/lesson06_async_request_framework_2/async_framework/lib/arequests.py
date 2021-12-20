from abc import ABC, abstractmethod, abstractproperty
import asyncio
from collections import Counter
from dataclasses import field, dataclass
from re import T
import time
from typing import List

from aiohttp import ClientResponseError, request


class Sentinel: pass

class ThrottledQueue(asyncio.Queue):
    "subclass asyncio.Queue i.e. import all behaviour"

    def __init__(self, per_second, debug=False, maxsize=0, *, loop=None, i=0):
        "Set up some extra vars and then call the original init"

        self.lock = asyncio.Lock()
        self.emergency_lock = asyncio.Lock()
        # TODO: use a Rater class/obj
        self.per_second = per_second
        self.last_get = time.time() # this is the fastest way... I think?
        self.debug = debug
        self.n_consumers = 0
        super(ThrottledQueue, self).__init__(maxsize=maxsize, loop=loop)

    async def notify(self, override: int=0):
        """
        Signals to the queue that an item is being retried,
        so pause any get()s by aquiring a lock and throttling before releasing
        """
        # This uses a 2nd lock, which the get() method must also aquire in order to return an item.
        # If we were to use self.lock here, then a call to notify() could be banked up behind many
        # get()s waiting to aquire the main lock.
        # This way, all of those get() requests can be queued while waiting for the lock, and if we
        # need to pause everything, then calling this method will immedidately lock the 2nd lock.
        # Any queued gets() will then be blocked by this as soon as they try and run
        async with self.emergency_lock:
            await self._throttle(override)

    def inc_consumer(self):
        self.n_consumers += 1

    def dec_consumer(self):
        self.n_consumers -= 1

    async def notify_until(self, until: int):
        async with self.emergency_lock:
            override = until-time.time()
            if override > 0:
                await self._throttle(override)
            else:
                print("SKIPPING")

    async def get(self):
        # If there are
        async with self.lock:
            async with self.emergency_lock:
                pass
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
    n_workers: int = 1

    def create_queue(self, debug=False):
        return ThrottledQueue(per_second=self.per_second, debug=debug)

    @abstractmethod
    async def response_unpacker(req_data, resp, *args):
        "Unpacks the response into individual items to put on a queue"

    @abstractmethod
    def request_builder(method, hostname, port, endpoint, payload=None):
        "Builds the *args and **kwargs to be passed to aiohttp.request()"

    @abstractmethod
    async def error_handler(e, q):
        "Handles API errors"

@dataclass
class AsyncEndpointPipeline:
    endpoints: List[AsyncEndpoint]
    initial: List[tuple]
    results: asyncio.Queue = field(default_factory=asyncio.Queue)

    async def async_run_pipeline(self):
        pipeline = []
        # For the first pipeline item, create the input queue containing the initial request/s
        in_q = await _fill_queue(ThrottledQueue(per_second=self.endpoints[0].per_second), self.initial)
        out_q = None

        for i, e in enumerate(self.endpoints):
            if i == len(self.endpoints)-1:
                out_q = self.results
            else:
                out_q = ThrottledQueue(per_second=self.endpoints[i+1].per_second)

            # TODO: how many workers is actually a reasonable amount to create?
            for j in range(e.n_workers):
                a = AsyncRequester(
                    in_q=in_q,
                    out_q=out_q,
                    req_builder=e.request_builder,
                    resp_unpacker=e.response_unpacker,
                    error_handler=e.error_handler,
                ).consumer(j)
                in_q.inc_consumer()
                pipeline.append(a)
            in_q = out_q

        await asyncio.gather(*pipeline)

    def run(self):
        return asyncio.run(self.async_run_pipeline())


@dataclass
class AsyncRequester:
    in_q: ThrottledQueue
    out_q: ThrottledQueue
    # TODO: each pipeline stage should only do 1 thing
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
                if d == Sentinel:
                    self.in_q.dec_consumer()
                    await self.in_q.put(Sentinel)
                    if self.in_q.n_consumers == 0:
                        await self.out_q.put(Sentinel)
                    print(self.log_prefix, f"worker {idx}", "exiting")
                    return
            retrying = False
            await asyncio.sleep(0)
            # TODO: put this aiottp.request stuff into the subclasses when separating the req_builder/resp_unpacker stuff
            t1 = time.time()
            async with request(*self.req_builder(*d)) as req:
                # print(self.log_prefix, f"worker {idx}", f"requesting {d}")
                resp = await req.read()
                try:
                    req.raise_for_status()
                except ClientResponseError as e:
                    print(f"Failure!! {e}")
                    self.cntr["failure"] += 1
                    await self.error_handler(e, self.in_q)
                    retrying = True
                    # TODO implement retry limit
                    continue
                result = await self.resp_unpacker(d, resp)
                for r in result:
                    await self.out_q.put(r)
                self.cntr["success"] += 1
            print(self.log_prefix, f"worker {idx}", "elapsed", time.time()-t1, f"response: {resp}")


async def _fill_queue(q, items):
    for i in items:
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
