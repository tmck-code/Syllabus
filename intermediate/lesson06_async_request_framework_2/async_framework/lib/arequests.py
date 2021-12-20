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
