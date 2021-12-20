#!/usr/bin/env python3

import asyncio
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
import random

from lib.arequests import ThrottledQueue, Sentinel, _fill_queue, unpack_queue
from abc import abstractmethod
from aiohttp import request, ClientResponseError


@dataclass
class Unpacker:
    "gets QueueItems from an asyncio.Queue, unpacks to another QueueItem, puts on a ThrottledQueue"

    in_q: asyncio.Queue
    out_q: ThrottledQueue

    @abstractmethod
    async def unpack(self, d: object) -> object:
        "Unpacks a queue object/transforms it for a ThrottledWorker"

    @abstractmethod
    async def handle_error(self, e):
        "Handles an error"

    async def run(self):
        print("Unpacker", self.__class__.__name__, "starting")
        while True:
            d = await self.in_q.get()
            if d == Sentinel:
                print("Unpacker", self.__class__.__name__, "exiting")
                await self.in_q.put(Sentinel)
                await self.out_q.put(Sentinel)
                return
            try:
                for el in await self.unpack(d):
                    print("unpacked", el)
                    await self.out_q.put(el)
            except Exception as e:
                await self.handle_error(self, e)


@dataclass
class ThrottledWorker:
    "gets QueueItems from a ThrottledQueue, builds into a requests, awaits response and puts on a asyncio.Queue"

    in_q: ThrottledQueue
    out_q: asyncio.Queue

    @abstractmethod
    async def work(self, d):
        "Does some work on a QueueItem and returns the result"

    @abstractmethod
    async def handle_error(self, e):
        "Handles an error"

    async def run(self):
        print("ThrottledWorker", self.__class__.__name__, "starting")
        retrying = False
        while True:
            if not retrying:
                d = await self.in_q.get()
                print("ThrottledWorker get()", d)
                if d == Sentinel:
                    print("ThrottledWorker", self.__class__.__name__, "exiting")
                    await self.in_q.put(Sentinel)
                    self.in_q.dec_consumer()
                    if self.in_q.n_consumers == 0:
                        await self.out_q.put(Sentinel)
                    return
            try:
                resp = await self.work(d)
            except Exception as e:
                await self.handle_error(e)
                retrying = True
                continue
            print("putting on queue", resp)
            await self.out_q.put(resp)
            retrying = False

from collections import namedtuple

AllCustomersQueueItem = namedtuple("all_customers_queue_item", ["method", "hostname", "port", "endpoint"])
CustomerByIDQueueItem = namedtuple("customers_by_id_queue_item", ["method", "hostname", "port", "endpoint", "id"])

@dataclass
class AllCustomersWorker(ThrottledWorker):

    async def work(self, d: AllCustomersQueueItem):
        async with request(d.method, f"http://{d.hostname}:{d.port}/{d.endpoint}") as req:
            resp = await req.read()
            req.raise_for_status()
            print(resp)
            return resp

    async def handle_error(self, e):
        print(f"HANDLING ERROR: {self.__class__.__name__}, {e}")
        if isinstance(e, ClientResponseError):
            if e.status == 429:
                await self.in_q.notify_until(time.time()+random.randint(3, 7))
            elif e.status == 503:
                await self.in_q.notify()

@dataclass
class AllCustomersUnpacker(Unpacker):

    base: AllCustomersQueueItem
    
    async def unpack(self, d) -> CustomerByIDQueueItem:
        print(d)
        return [CustomerByIDQueueItem(*tuple(self.base), i) for i in json.loads(d)]

@dataclass
class CustomerByIDWorker(ThrottledWorker):

    async def work(self, d: CustomerByIDQueueItem):
        async with request(d.method, f"http://{d.hostname}:{d.port}/{d.endpoint}/{d.id}") as req:
            resp = await req.read()
            req.raise_for_status()  
            return resp

    async def handle_error(self, e):
        print(f"HANDLING ERROR: {self.__class__.__name__}, {e}")
        if isinstance(e, ClientResponseError):
            if e.status == 429:
                await self.in_q.notify_until(time.time()+random.randint(3, 7))
            elif e.status == 503:
                await self.in_q.notify()

async def run_pipeline():
    all_customers_q = await _fill_queue(ThrottledQueue(per_second=1), [AllCustomersQueueItem("get", "0.0.0.0", "8080", "items")])
    all_customers_q.inc_consumer()
    customers_by_id_q = ThrottledQueue(per_second=20)
    t, results = asyncio.Queue(), asyncio.Queue()

    await asyncio.gather(
        AllCustomersWorker(in_q=all_customers_q, out_q=t).run(),
        AllCustomersUnpacker(in_q=t, out_q=customers_by_id_q, base=AllCustomersQueueItem("get", "0.0.0.0", "8080", "items")).run(),
        *[CustomerByIDWorker(in_q=customers_by_id_q, out_q=results).run() for _ in range(40)],
    )
    for _ in range(40):
        customers_by_id_q.inc_consumer()
    return results

res = asyncio.run(run_pipeline())
l = unpack_queue(res)

print(l, len(l))
