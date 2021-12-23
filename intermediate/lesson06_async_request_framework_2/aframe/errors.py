from dataclasses import field, dataclass
from typing import Any, Dict, Generic, Iterable, Iterator, List, TypeVar, Type, cast
from uuid import uuid4

from aiohttp import ClientResponseError, ClientTimeout
from slugify import slugify


T = TypeVar("T")


class APIExceptionMetadata(Generic[T]):
    def should_retry(self, e: T) -> bool:
        "Should the action be retried?"
        return False

    def slugify_exception(self, e: T) -> List[str]:
        return ["unknown_exception", str(e)]

    def should_record_stack(self, e: T) -> bool:
        return False

    def unpack(self, e: T) -> Iterator[T]:
        "Unpacks nested error objects"
        yield from []


class ExceptionMeta(APIExceptionMetadata[Exception]):
    def should_record_stack(self, e: T) -> bool:
        # for an unknown exception, we do actually want to record the stack trace
        return True


class APIErrorRegistry:
    exceptions: Dict[Type, APIExceptionMetadata] = {
        Exception: ExceptionMeta(),
    }

    def _get_exception_meta(self, e: Exception) -> APIExceptionMetadata:
        for klass in self.__superclasses(e):
            if klass in self.exceptions:
                return self.exceptions[klass]
        else:
            # this shouldn't  be reachable as long as e is an Exception
            # and Exception is a key in self.exceptions
            return self.exceptions[Exception]

    def __superclasses(self, obj: Any) -> List[Type]:
        'Return the superclasses of a class in Method Resolution Order (MRO), ie "nearest" superclass first'
        return cast(List[Type], obj.__class__.mro())

    def unpack(self, e: Exception) -> Iterator[T]:
        return self._get_exception_meta(e).unpack(e)

    def get_slug(self, e: Exception):
        return self._get_slug_internal(
            *self._get_exception_meta(e).slugify_exception(e)
        )

    def _get_slug_internal(self, *args: str) -> str:
        res = slugify("_".join(args), separator="_", max_length=160)
        return cast(str, res)

    def should_retry(self, e: Exception) -> bool:
        return self._get_exception_meta(e).should_retry(e)

    def should_record_stack(self, e: Exception) -> bool:
        return self._get_exception_meta(e).should_record_stack(e)


T = TypeVar("T")

@dataclass
class ReservoirSampler(Generic[T]):
    """Randomly sample from a stream of unknown length.
    https://en.wikipedia.org/wiki/Reservoir_sampling
    """

    size: int = 10
    samples: List[T] = field(default_factory=list)

    def __post_init__(self):
        self.counter: int = 0

    def normalise(self, sample: T) -> None:
        return sample

    def add(self, sample: T) -> None:
        """Attempts to add a sample to the reservoir. If the reservoir is full of samples, there is
        a chance it will be added by replacing an existing sample, with gradually decreasing
        probability
        """
        sample = self.normalise(sample)
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

@dataclass
class ErrorSampler(ReservoirSampler):

    registry: APIErrorRegistry = field(default_factory=APIErrorRegistry)

    def normalise(self, sample: T) -> None:
        return self.registry.get_slug(sample)
