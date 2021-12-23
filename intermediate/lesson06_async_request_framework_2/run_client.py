#!/usr/bin/env python3

import asyncio
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
import random
from collections import namedtuple

from aframe.arequests import ThrottledQueue, Sentinel, _fill_queue
from abc import abstractmethod
from aiohttp import request, ClientResponseError


@dataclass
class Unpacker:
    "gets QueueItems from an asyncio.Queue, unpacks to another QueueItem, puts on a ThrottledQueue"

    key: str
    in_q: asyncio.Queue
    out_q: ThrottledQueue

    @abstractmethod
    async def unpack(self, d: namedtuple) -> namedtuple:
        "Unpacks a queue object/transforms it for a ThrottledWorker"

    @abstractmethod
    async def handle_error(self, e):
        "Handles an error"

    def log(self, body: dict):
        print(json.dumps({self.__class__.__name__: self.key, **body}))

    async def run(self):
        self.log({"state": "starting"})
        while True:
            d = await self.in_q.get()
            if d == Sentinel:
                self.log({"state": "exiting"})
                await self.in_q.put(Sentinel)
                await self.out_q.put(Sentinel) # there will only ever be 1 unpacker per stage, so it's safe to
                                               # just put a sentinel on the out_q
                return
            try:
                for el in await self.unpack(d):
                    self.log({"unpacked": el})
                    await self.out_q.put(el)
            except Exception as e:
                await self.handle_error(self, e)


@dataclass
class ThrottledWorker:
    "gets QueueItems from a ThrottledQueue, builds into a requests, awaits response and puts on a asyncio.Queue"

    key: str
    in_q: ThrottledQueue
    out_q: asyncio.Queue

    def __post_init__(self):
        self.in_q.inc_consumer()

    @abstractmethod
    async def work(self, d):
        "Does some work on a QueueItem and returns the result"

    @abstractmethod
    async def handle_error(self, e):
        "Handles an error"

    def log(self, body: dict):
        print(json.dumps({self.__class__.__name__: self.key, **body}))

    async def run(self):
        self.log({"state": "starting"})
        retrying = False
        while True:
            if not retrying:
                d = await self.in_q.get()
                if d == Sentinel:
                    self.log({"state": "exiting", "remaining": self.in_q.n_consumers-1})
                    await self.in_q.put(Sentinel)
                    self.in_q.dec_consumer()
                    if self.in_q.n_consumers == 0:
                        await self.out_q.put(Sentinel)
                    return
            t = time.time()
            try:
                resp = await self.work(d)
            except Exception as e:
                await self.handle_error(e)
                retrying = True
                continue
            self.log({"req": d, "duration": time.time()-t})
            await self.out_q.put(resp)
            retrying = False


@dataclass
class Finisher:
    """
    Takes items from an asyncio.Queue and transfers to the synchronous work
    e.g. printing to stdout, collecting to a list, writing to file etc.
    """

    in_q: asyncio.Queue

    @abstractmethod
    async def run(self):
        "Awaits each item in the queue and puts it somewhere"

import sys

@dataclass
class PrintFinisher(Finisher):

    stream: object = sys.stderr

    async def run(self):
        while True:
            d = await self.in_q.get()
            if d == Sentinel:
                await self.in_q.put(Sentinel)
                return
            print(d.decode(), file=self.stream)


from collections import namedtuple

AllCustomersQueueItem = namedtuple("all_customers_queue_item", ["method", "hostname", "port", "endpoint"])
CustomerByIDQueueItem = namedtuple("customers_by_id_queue_item", ["method", "hostname", "port", "endpoint", "id"])

@dataclass
class AllCustomersWorker(ThrottledWorker):

    async def work(self, d: AllCustomersQueueItem):
        async with request(d.method, f"http://{d.hostname}:{d.port}/{d.endpoint}") as req:
            resp = await req.read()
            req.raise_for_status()
            return resp

    async def handle_error(self, e):
        self.log({"error": str(e)})
        if isinstance(e, ClientResponseError):
            if e.status == 429:
                await self.in_q.notify_until(time.time()+random.randint(3, 7))
            elif e.status == 503:
                await self.in_q.notify()

@dataclass
class AllCustomersUnpacker(Unpacker):

    base: AllCustomersQueueItem

    async def unpack(self, d) -> CustomerByIDQueueItem:
        return [CustomerByIDQueueItem(*tuple(self.base), i) for i in json.loads(d)]

@dataclass
class CustomerByIDWorker(ThrottledWorker):

    async def work(self, d: CustomerByIDQueueItem):
        async with request(d.method, f"http://{d.hostname}:{d.port}/{d.endpoint}/{d.id}") as req:
            resp = await req.read()
            req.raise_for_status()
            return resp

    async def handle_error(self, e):
        self.log({"error": str(e)})
        if isinstance(e, ClientResponseError):
            if e.status == 429:
                await self.in_q.notify_until(time.time()+random.randint(3, 7))
            elif e.status == 503:
                await self.in_q.notify()

async def run_pipeline():
    all_customers_q = await _fill_queue(ThrottledQueue(per_second=1), [AllCustomersQueueItem("get", "0.0.0.0", "8080", "items")])
    customers_by_id_q = ThrottledQueue(per_second=20)
    t, results = asyncio.Queue(), asyncio.Queue()

    await asyncio.gather(
        AllCustomersWorker(key="0", in_q=all_customers_q, out_q=t).run(),
        AllCustomersUnpacker(key="0", in_q=t, out_q=customers_by_id_q, base=AllCustomersQueueItem("get", "0.0.0.0", "8080", "items")).run(),
        *[CustomerByIDWorker(key=str(i), in_q=customers_by_id_q, out_q=results).run() for i in range(40)],
        PrintFinisher(in_q=results).run(),
    )

    return results

asyncio.run(run_pipeline())
