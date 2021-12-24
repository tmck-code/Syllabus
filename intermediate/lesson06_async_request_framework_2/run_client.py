#!/usr/bin/env python3

import asyncio
import json
from dataclasses import dataclass, field
from abc import ABC
from os import error
import time
import random
from collections import namedtuple
import sys

from abc import abstractmethod
from aiohttp import request, ClientResponseError

from aframe.arequests import ThrottledQueue, ThrottledWorker, Unpacker, Finisher, Sentinel, _fill_queue
from aframe.stats import ActionStats
from aframe.errors import ExceptionRegistry

from copy import deepcopy
import json
from multidict import CIMultiDictProxy

class RequestExceptionRegistry(ExceptionRegistry):
    exceptions = deepcopy(ExceptionRegistry.exceptions)

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
        # TODO: slugify error/implement all error metaclasses from customer-api
        self.log({"error": str(e)})
        if isinstance(e, ClientResponseError):
            if e.status == 429:
                await self.in_q.notify_until(time.time()+random.randint(3, 7))
            elif e.status == 503:
                await self.in_q.notify()

@dataclass
class AllCustomersUnpacker(Unpacker):

    base: AllCustomersQueueItem

    async def unpack(self, d: str) -> CustomerByIDQueueItem:
        return [CustomerByIDQueueItem(*tuple(self.base), i) for i in json.loads(d)]

error_registry: RequestExceptionRegistry = field(default_factory=RequestExceptionRegistry)


@dataclass
class CustomerByIDWorker(ThrottledWorker):

    stats: ActionStats
    slug: str = "customer_by_id"

    async def work(self, d: CustomerByIDQueueItem) -> str:
        async with request(d.method, f"http://{d.hostname}:{d.port}/{d.endpoint}/{d.id}") as req:
            resp = await req.read()
            req.raise_for_status()
            self.stats.record_success(action_slug=self.slug, success=1)
            return resp

    async def handle_error(self, e):
        self.log({"error": str(e)})
        self.stats.record_error(action_slug=self.slug, error=e)
        if isinstance(e, ClientResponseError):
            if e.status == 429:
                await self.in_q.notify_until(time.time()+random.randint(3, 7))
            elif e.status == 503:
                await self.in_q.notify()

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

@dataclass
class PipelineOfItems:
    initial_queue: asyncio.Queue


async def run_pipeline():
    all_customers_q = await _fill_queue(ThrottledQueue(per_second=1), [AllCustomersQueueItem("get", "0.0.0.0", "8080", "items")])
    customers_by_id_q = ThrottledQueue(per_second=20)
    t, results = asyncio.Queue(), asyncio.Queue()
    stats = ActionStats(error_registry=ExceptionRegistry())
    w = AllCustomersWorker(key="0", in_q=all_customers_q, out_q=t)
    wks = [CustomerByIDWorker(key=str(i), in_q=customers_by_id_q, out_q=results, stats=stats) for i in range(40)]

    await asyncio.gather(
        w.run(),
        AllCustomersUnpacker(key="0", in_q=t, out_q=customers_by_id_q, base=AllCustomersQueueItem("get", "0.0.0.0", "8080", "items")).run(),
        *[i.run() for i in wks],
        PrintFinisher(in_q=results).run(),
    )

    return (results, stats)

results, stats = asyncio.run(run_pipeline())

print(results)
print(stats)
print(json.dumps(stats.as_dict(), indent=2))