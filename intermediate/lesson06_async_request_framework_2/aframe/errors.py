from __future__ import annotations

from dataclasses import dataclass
from random import randint
from typing import (
    Callable,
    Generic,
    Iterable,
    List,
    Optional,
    TypeVar,
)

T = TypeVar("T")


class ReservoirSampler(Generic[T]):
    """Randomly sample from a stream of unknown length.
    https://en.wikipedia.org/wiki/Reservoir_sampling
    """

    def __init__(self, size: int = 10):
        self.size = size
        self.counter = 0
        self.samples: List[T] = []

    def add(self, sample: T) -> None:
        """Attempts to add a sample to the reservoir. If the reservoir is full of samples, there is
        a chance it will be added by replacing an existing sample, with gradually decreasing
        probability
        """
        if self.counter < self.size:
            self.samples.append(sample)
        else:
            k = randint(0, self.counter)
            if k < self.size:
                self.samples[k] = sample
        self.counter += 1

    def extend(self, samples: Iterable[T]) -> None:
        "Attempts to add each sample in an iterable to the reservoir"
        for s in samples:
            self.add(s)


# Response pydantic model

class CountWithExamples(Generic[T]):
    count: int = 0
    examples: List[T]


# Why isn't this a subclass of CountWithExamples?
# https://github.com/samuelcolvin/pydantic/issues/947
class CountWithExamplesAndReason(Generic[T]):
    count: int = 0
    examples: List[T]
    reason: str


@dataclass
class ExampleCounter(Generic[T]):
    examples: ReservoirSampler[T]
    count: int = 0

    @classmethod
    def sample(cls, size: int = 10) -> ExampleCounter[T]:
        return cls(examples=ReservoirSampler(size))

    @classmethod
    def factory(cls, size: int = 10) -> Callable[[], ExampleCounter[T]]:
        def wrapped():
            return cls.sample(size)

        return wrapped

    def increment(self, example: Optional[T]) -> None:
        self.count += 1
        if example is not None:
            self.examples.add(example)

    def output(self) -> CountWithExamples[T]:
        return CountWithExamples(
            count=self.count, examples=list(set(self.examples.samples))
        )

    def output_with_reason(self, reason: str) -> CountWithExamplesAndReason[T]:
        return CountWithExamplesAndReason(
            count=self.count, examples=list(set(self.examples.samples)), reason=reason
        )

