#!/usr/bin/env python3

import asyncio
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import abc
from os import pipe
from typing import List

from lib.arequests import _fill_queue, ThrottledQueue, AsyncRequester, unpack_queue


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


@dataclass
class AllCustomers(AsyncEndpoint):

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
        result = asyncio.run(self.async_run_pipeline())
        print(len(result), result)

AsyncEndpointPipeline(
    endpoints=[
        AllCustomers(per_second=1),
        CustomerByID(per_second=10)
    ],
    initial=[
        ("get", "0.0.0.0", "8080", "items")
    ]
).run_pipeline()

# async def main():
#     t = await _fill_queue(ThrottledQueue(per_second=1), [("get", "0.0.0.0", "8080", "items")])
#     t2 = ThrottledQueue(per_second=10, debug=True)
#     res = asyncio.Queue()

#     print(t, t2, res)

#     all_customers_req = AsyncRequester(
#         in_q          = t,
#         out_q         = t2,
#         req_builder   = base_request_builder,
#         resp_unpacker = base_response_unpacker,
#         error_handler = handle_error,
#     )

#     customers_by_id_req = AsyncRequester(
#         in_q          = t2,
#         out_q         = res,
#         req_builder   = id_request_builder,
#         resp_unpacker = id_response_unpacker,
#         error_handler = handle_error,
#     )
#     print("Running pipeline")

#     await asyncio.gather(
#         customers_by_id_req.consumer(0),
#         all_customers_req.consumer(0),
#     )
#     return res

# if __name__ == '__main__':
#     res = asyncio.run(main())
#     print(unpack_queue(res))
