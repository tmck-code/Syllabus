#!/usr/bin/env python3

import asyncio
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import abc
from os import pipe
from typing import List
import time
import random

from lib.arequests import AsyncEndpointPipeline, AsyncEndpoint, ThrottledQueue, unpack_queue, Sentinel
from abc import abstractmethod
@dataclass
class Unpacker:
    "gets QueueItems from an asyncio.Queue, unpacks to another QueueItem, puts on a ThrottledQueue"

    in_q: asyncio.Queue
    out_q: ThrottledQueue

    @abstractmethod
    async def unpack(self, d: object) -> object:
        "Unpacks a queue object/transforms it for a ThrottledWorker"

    async def run(self):
        while True:
            d = await self.in_q.get()
            for el in self.unpack(d):
                await self.out_q.put(el)


@dataclass
class ThrottledWorker:
    "gets QueueItems from a ThrottledQueue, builds into a requests, awaits response and puts on a asyncio.Queue"

    in_q: ThrottledQueue
    out_q: asyncio.Queue

    @abstractmethod
    async def work(self, d):
        "Does some work on a QueueItem and returns the result"

    async def run(self):
        while True:
            d = await self.in_q.get()
            resp = await self.work(d)
            await self.out_q.put(d)


@dataclass
class AllCustomers(AsyncEndpoint):

    async def response_unpacker(self, req_data, resp):
        print("+++", *req_data, resp)
        return [(*req_data, i) for i in json.loads(resp)]

    def request_builder(self, method, hostname, port, endpoint, *args):
        return (method, f"http://{hostname}:{port}/{endpoint}")

    async def error_handler(self, e, q):
        print(f"HANDLING ERROR: {e}")
        if e.status == 429:
            await q.notify_until(time.time()+random.randint(3, 7))
        elif e.status == 503:
            await q.notify()


@dataclass
class CustomerByID(AsyncEndpoint):

    async def response_unpacker(self, req_data, resp):
        return [(resp,)]

    def request_builder(self, method, hostname, port, endpoint, i):
        return (method, f"http://{hostname}:{port}/{endpoint}/{i}")

    async def error_handler(self, e, q):
        print(f"HANDLING ERROR: {e}")
        if e.status == 429:
            await q.notify_until(time.time()+random.randint(3, 7))
        elif e.status == 503:
            await q.notify()


pipeline = AsyncEndpointPipeline(
    endpoints=[
        AllCustomers(per_second=1),
        CustomerByID(per_second=20, n_workers=40),
    ],
    initial=[
        ("get", "0.0.0.0", "8080", "items")
    ]
)
pipeline.run()
results = unpack_queue(pipeline.results)

for r in results:
    if r == Sentinel:
        continue
    print(r[0].decode())
print(len(results))
