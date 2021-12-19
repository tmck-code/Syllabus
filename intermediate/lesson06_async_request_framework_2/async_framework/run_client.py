#!/usr/bin/env python3

import asyncio
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import abc
from os import pipe
from typing import List

from lib.arequests import AsyncEndpointPipeline, AsyncEndpoint


@dataclass
class AllCustomers(AsyncEndpoint):

    @property
    def per_second(self):
        return 1

    async def response_unpacker(self, req_data, resp, queue):
        for i in json.loads(resp):
            print("+++", *req_data, i)
            await queue.put((*req_data, i))

    def request_builder(self, method, hostname, port, endpoint, *args):
        return (method, f"http://{hostname}:{port}/{endpoint}")

    async def error_handler(self, e, q):
        print(f"HANDLING ERROR: {e}")
        if e.status == 429:
            await q.notify()
        elif e.status == 503:
            await q.notify()


@dataclass
class CustomerByID(AsyncEndpoint):

    @property
    def per_second(self):
        return 50

    async def response_unpacker(self, req_data, resp, queue):
        await queue.put(resp,)

    def request_builder(self, method, hostname, port, endpoint, i):
        return (method, f"http://{hostname}:{port}/{endpoint}/{i}")

    async def error_handler(self, e, q):
        print(f"HANDLING ERROR: {e}")
        if e.status == 429:
            await q.notify()
        elif e.status == 503:
            await q.notify()


AsyncEndpointPipeline(
    endpoints=[
        AllCustomers(),
        CustomerByID(),
    ],
    initial=[
        ("get", "0.0.0.0", "8080", "items")
    ]
).run_pipeline()
