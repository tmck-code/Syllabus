#!/usr/bin/env python3

import asyncio
import json

from lib.arequests import _fill_queue, ThrottledQueue, AsyncRequester

async def id_response_unpacker(req_data, resp, queue, *args):
    await queue.put((0, (resp,)))

async def base_response_unpacker(req_data, resp, queue):
    for i in json.loads(resp):
        print((0, (*req_data, i)))
        await queue.put((0, (*req_data, i)))

def id_request_builder(method, hostname, port, endpoint, i):
    return (method, f"http://{hostname}:{port}/{endpoint}/{i}")

def base_request_builder(method, hostname, port, endpoint):
    return (method, f"http://{hostname}:{port}/{endpoint}")

async def handle_error(e, q):
    print(f"HANDLING ERROR: {e}")
    if e.status == 429:
        q.retry()
    elif e.status == 503:
        q.lock(10)

async def main():
    t = await _fill_queue(asyncio.Queue(), [("get", "0.0.0.0", "8080", "items")])
    t2 = ThrottledQueue(per_second=100)
    res = asyncio.Queue()

    print(t, t2, res)

    all_customers_req = AsyncRequester(
        in_q          = t,
        out_q         = t2,
        req_builder   = base_request_builder,
        resp_unpacker = base_response_unpacker,
        error_handler = handle_error,
    )

    customers_by_id_req = AsyncRequester(
        in_q          = t2,
        out_q         = res,
        req_builder   = id_request_builder,
        resp_unpacker = id_response_unpacker,
        error_handler = handle_error,
    )
    print("Running pipeline")

    await asyncio.gather(
        all_customers_req.consumer(0),
        customers_by_id_req.consumer(0),
    )

if __name__ == '__main__':
    asyncio.run(main())
