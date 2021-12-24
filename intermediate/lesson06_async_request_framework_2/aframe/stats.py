from __future__ import annotations

from dataclasses import dataclass, field, asdict
from random import randint
from typing import (
    Dict,
    Union,
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    TypeVar,
)
from traceback import TracebackException
from abc import abstractmethod
from collections import Counter, defaultdict

from aiohttp import ClientResponseError
import json

from slugify import slugify

from aframe.errors import ExceptionRegistry

T = TypeVar("T")

SAMPLE_SIZE = 10

@dataclass
class ReservoirSampler(Generic[T]):
    """Randomly sample from a stream of unknown length.
    https://en.wikipedia.org/wiki/Reservoir_sampling
    """

    size: int = 10
    counter: int = 0
    counts: Counter = field(default_factory=Counter)
    samples: List[T] = field(default_factory=list)

    def add(self, sample: T, slug: str = '') -> None:
        """Attempts to add a sample to the reservoir. If the reservoir is full of samples, there is
        a chance it will be added by replacing an existing sample, with gradually decreasing
        probability
        """
        if not slug:
            slug = sample.__class__.__name__
        self.counts[slug] += 1
        if self.counter < self.size:
            self.samples.append({slug: sample})
        else:
            k = randint(0, self.counter)
            if k < self.size:
                self.samples[k] = sample
        self.counter += 1

    def extend(self, samples: Iterable[T]) -> None:
        "Attempts to add each sample in an iterable to the reservoir"
        for s in samples:
            self.add(s)

    def serialise(self, indent=None):
        return json.dumps([self.as_dict(e) for e in self.samples], indent=2)

    @staticmethod
    def _factory():
        return ReservoirSampler(SAMPLE_SIZE)

    def as_dict(self):
        return self.__dict__

@dataclass
class Stats(Generic[T]):
    counts: Counter = field(default_factory=Counter)
    error_detail: ReservoirSampler = field(default_factory=ReservoirSampler)

    def error_rate(self):
        return self.counts["errors"] / self.counts["total"]

    def record_success(self, success=1):
        self.counts["success"] += success
        self.counts["total"] += 1

    def record_error(self, error, slug=''):
        self.counts["errors"] += 1
        self.counts["total"] += 1
        self.error_detail.add(error, slug)

    def as_dict(self):
        return {
            "counts": self.counts,
            "error_detail": self.error_detail.as_dict(),
        }

def stats_factory():
    return defaultdict(Stats)

@dataclass
class ActionStats:
    error_registry: ExceptionRegistry
    actions: Dict[str, Stats] = field(default_factory=stats_factory)

    def record_success(self, action_slug: str, success: int=1):
        self.actions[action_slug].record_success(success)

    def record_error(self, action_slug: str, error):
        self.actions[action_slug].record_error(self.error_registry.serialise_exception(error), self.error_registry.slugify_exception(error))

    def as_dict(self):
        return {k: v.as_dict() for k, v in self.actions.items()}