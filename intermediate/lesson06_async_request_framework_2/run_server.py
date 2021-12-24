#!/usr/bin/env python3

from aframe.aserver import AServer, Rater

AServer(
    rate_limit=Rater(600, 60),
    max_items=700,
).run()
