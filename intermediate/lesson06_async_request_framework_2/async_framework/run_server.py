#!/usr/bin/env python3

from lib.aserver import AServer, Rater

AServer(
    rate_limit=Rater(600, 60),
    max_items=2_000,
).run()
