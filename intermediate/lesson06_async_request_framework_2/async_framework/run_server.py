#!/usr/bin/env python3

from lib.aserver import AServer, Rater

AServer(
    rate_limit=Rater(6_000, 60),
    max_items=1_000
).run()
