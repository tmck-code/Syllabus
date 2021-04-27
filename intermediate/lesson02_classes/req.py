import logging
from dataclasses import dataclass, field
from time import time
from typing import Callable
import functools
import json

from tenacity import (
    retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential
)

LOG = logging.getLogger(__name__)
logging.basicConfig()

DEFAULT_MAX_ATTEMPTS = 10
MAX_WAIT_SECONDS = 60
MAX_ATTEMPTS = 5

DEFAULT_RETRY_EXCEPTIONS = (ConnectionError,)

def default_handler(d):
    LOG.info(d)

@dataclass
class Timer:
    handler: Callable[[dict], None]
    start_time: float = field(default_factory=time)
    stop_time:  float = 0.0

    def duration(self, current_time=time()):
        return current_time - self.start_time

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.handler(self.as_dict(time()))

    def as_dict(self, stop_time):
        return {
            'start_time': self.start_time,
            'stop_time': stop_time,
            'duration': self.duration(stop_time).total_seconds(),
        }

def log_decorator(log_enabled):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if log_enabled:
                LOG.info("Calling Function: " + func.__name__)
            result = func(*args, **kwargs)
            LOG.info(result)
            return result
        return wrapper
    return actual_decorator

@retry(
    retry=retry_if_exception_type(DEFAULT_RETRY_EXCEPTIONS),
    stop=(stop_after_attempt(MAX_ATTEMPTS)),
    wait=wait_random_exponential(max=MAX_WAIT_SECONDS),
    reraise=True
)
@log_decorator(True)
def gen_request(client, endpoint, params):
    with Timer() as timer:
        LOG.debug(f'Request for endpoint {endpoint}: {params}')
        resp = client.get(endpoint, params=params)

        resp.raise_for_status()
        return json.loads(resp.content)