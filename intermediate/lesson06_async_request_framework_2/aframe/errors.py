from __future__ import annotations

from dataclasses import dataclass, field
from random import randint
from typing import (
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    TypeVar,
)
from abc import abstractmethod

from aiohttp import ClientResponseError
import json

from slugify import slugify

T = TypeVar("T")


class ReservoirSampler(Generic[T]):
    """Randomly sample from a stream of unknown length.
    https://en.wikipedia.org/wiki/Reservoir_sampling
    """

    def __init__(self, size: int = 10):
        self.size = size
        self.count = 0
        self.samples: List[T] = []

    def add(self, sample: T) -> None:
        """Attempts to add a sample to the reservoir. If the reservoir is full of samples, there is
        a chance it will be added by replacing an existing sample, with gradually decreasing
        probability
        """
        if self.count < self.size:
            self.samples.append(sample)
        else:
            k = randint(0, self.count)
            if k < self.size:
                self.samples[k] = sample
        self.count += 1

    def extend(self, samples: Iterable[T]) -> None:
        "Attempts to add each sample in an iterable to the reservoir"
        for s in samples:
            self.add(s)

    @classmethod
    def combine(cls, examples: List[cls]):
        combined = cls(100)
        for e in examples:
            combined.extend(e.samples)
        return combined

class RequestErrorExampleCounter(ReservoirSampler[T]):

    def as_dict(self, e: ClientResponseError):
        return {
            "request": {"url": str(e.request_info.real_url), "method": e.request_info.method}, #, "headers": dict(e.request_info.headers)},
            "status":  e.status,
            "message": e.message,
        }

    def serialise(self, indent=None):
        return json.dumps([self.as_dict(e) for e in self.samples], indent=2)