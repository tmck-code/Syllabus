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

    def add(self, example: Optional[T]) -> None:
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

    @staticmethod
    def combine(examples: List[ExampleCounter]):
        count = 0
        ex = []
        for e in examples:
            count += e.count
            ex.extend(e.examples.samples)

        return ex



# import json
# from copy import deepcopy
# from dataclasses import dataclass
# from typing import (
#     Iterator,
#     List,
#     Optional,
# )

# import structlog
# from facebook_business.exceptions import FacebookRequestError

# from customer_api.activations.activation_errors import (
#     ActivationErrorRegistry,
#     ActivationExceptionMetadata,
# )


# @dataclass
# class FacebookOfflineEventErrorData(Exception):
#     event: Optional[dict] = None
#     event_index: Optional[int] = None
#     message: Optional[str] = ""
#     type: str = ""
#     code: Optional[int] = None

#     @staticmethod
#     def from_dict(dct):
#         return FacebookOfflineEventErrorData(**dct)


# class FacebookOfflineEventErrorDataMeta(
#     ActivationExceptionMetadata[FacebookOfflineEventErrorData]
# ):
#     def should_retry(self, e: FacebookOfflineEventErrorData) -> bool:
#         return True

#     def slugify_exception(self, e: FacebookOfflineEventErrorData) -> List[str]:
#         try:
#             return ["fb_request_error_data", e.type, str(e.code)]
#         except Exception as err:
#             return ["fb_request_error_data_error", repr(err)]


# class FacebookRequestErrorMeta(ActivationExceptionMetadata[FacebookRequestError]):
#     def should_retry(self, e: FacebookRequestError) -> bool:
#         transient_error = e.api_transient_error()
#         if isinstance(transient_error, bool):
#             return transient_error
#         else:
#             return False

#     def unpack(
#         self, e: FacebookRequestError
#     ) -> Iterator[FacebookOfflineEventErrorData]:
#         for _i, raw_data in e.body()["error"].get("error_data", {}).items():
#             yield FacebookOfflineEventErrorData(**raw_data)

#     def slugify_exception(self, e: Exception) -> List[str]:
#         try:
#             error = FacebookOfflineEventErrorData.from_dict(e)
#             return ["fb_request_error", error.type, str(error.code)]
#         except Exception as err:
#             return ["fb_request_error_error", repr(err)]


# class FacebookActivationErrorRegistry(ActivationErrorRegistry):
#     exceptions = deepcopy(ActivationErrorRegistry.exceptions)
#     exceptions[FacebookRequestError] = FacebookRequestErrorMeta()
#     exceptions[FacebookOfflineEventErrorData] = FacebookOfflineEventErrorDataMeta()



# class ActivationErrorRegistry:
#     exceptions: Dict[Type, ActivationExceptionMetadata] = {
#         Exception: ExceptionMeta(),
#         KeyError: KeyErrorMeta(),
#         ValueError: ValueErrorMeta(),
#     }

#     def _get_exception_meta(self, e: Exception) -> ActivationExceptionMetadata:
#         for klass in self.__superclasses(e):
#             if klass in self.exceptions:
#                 return self.exceptions[klass]
#         else:
#             # this shouldn't  be reachable as long as e is an Exception
#             # and Exception is a key in self.exceptions
#             return self.exceptions[Exception]

#     def __superclasses(self, obj: Any) -> List[Type]:
#         'Return the superclasses of a class in Method Resolution Order (MRO), ie "nearest" superclass first'
#         return cast(List[Type], obj.__class__.mro())

#     def unpack(self, e: Exception) -> Iterator[T]:
#         return self._get_exception_meta(e).unpack(e)

#     def get_slug(self, e: Exception):
#         return self._get_slug_internal(
#             *self._get_exception_meta(e).slugify_exception(e)
#         )

#     def _get_slug_internal(self, *args: str) -> str:
#         res = slugify("_".join(args), separator="_", max_length=160)
#         return cast(str, res)

#     def should_retry(self, e: Exception) -> bool:
#         return self._get_exception_meta(e).should_retry(e)

#     def recoverable(self, e: Exception) -> bool:
#         return self._get_exception_meta(e).recoverable(e)

#     def should_record_stack(self, e: Exception) -> bool:
#         return self._get_exception_meta(e).should_record_stack(e)