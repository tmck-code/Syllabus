
t = asyncio.run(_fill_queue(ThrottledQueue(per_second=1), [("get", "0.0.0.0", "8080", "items")]))
t2 = ThrottledQueue(per_second=100)
res = asyncio.Queue()

all_customers_req = AsyncRequester(
    in_q          = t,
    out_q         = t2,
    req_builder   = base_request_builder,
    resp_unpacker = base_response_unpacker,
    error_handler = handle_error,
    log_prefix    = "+++",
)

customers_by_id_req = AsyncRequester(
    in_q          = t2,
    out_q         = res,
    req_builder   = id_request_builder,
    resp_unpacker = id_response_unpacker,
    error_handler = handle_error,
    log_prefix    = "___",
)

asyncio.run(
    asyncio.gather(
        asyncio.create_task(all_customers_req.consumer(0)),
        asyncio.create_task(customers_by_id_req.consumer(0)),
        asyncio.create_task(customers_by_id_req.consumer(1)),
    )
)
