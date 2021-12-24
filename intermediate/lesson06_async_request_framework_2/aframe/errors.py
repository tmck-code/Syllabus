from typing import Any, Dict, Iterator, List, Generic, Type, TypeVar, cast

from aiohttp import ClientResponseError, ClientTimeout
from slugify import slugify


T = TypeVar("T")

class ExceptionMetadata(Generic[T]):
    def should_retry(self, e: T) -> bool:
        "Should the action be retried?"
        return False

    def slugify_exception(self, e: T) -> List[str]:
        return ["unknown_exception", str(e)]

    def serialise_exception(self, e: T) -> Dict[str, str]:
        return {"message": str(e)}

    def should_record_stack(self, e: T) -> bool:
        return False

    def recoverable(self, e: T) -> bool:
        "Should the activation continue?"
        return True

    def unpack(self, e: T) -> Iterator[T]:
        "Unpacks nested error objects"
        yield from []


class ExceptionMeta(ExceptionMetadata[Exception]):
    def should_record_stack(self, e: T) -> bool:
        # for an unknown exception, we do actually want to record the stack trace
        return True


class ClientResponseErrorMeta(ExceptionMetadata[ClientResponseError]):
    def slugify_exception(self, e: ClientResponseError) -> List[str]:
        # Note that the string represtentation of KeyError is the missing key in single quotes
        return ["client_response_error", str(e.code)]

    def serialise_exception(self, e: T) -> Dict[str, str]:
        return {
            "status":  e.status,
            "message": e.message,
            "url":     str(e.request_info.real_url)
        }

    def should_record_stack(self, e: T) -> bool:
        return True


class ClientTimeoutMeta(ExceptionMetadata[ClientTimeout]):
    def slugify_exception(self, e: ClientTimeout) -> List[str]:
        return ["client_timeout", str(e.code)]

    def should_record_stack(self, e: T) -> bool:
        return True


class ExceptionRegistry:
    exceptions: Dict[Type, ExceptionMetadata] = {
        Exception: ExceptionMeta(),
        ClientResponseError: ClientResponseErrorMeta(),
        ClientTimeout: ClientTimeoutMeta(),
    }

    def _get_exception_meta(self, e: Exception) -> ExceptionMetadata:
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

    def slugify_exception(self, e: Exception):
        return self._get_slug_internal(
            *self._get_exception_meta(e).slugify_exception(e)
        )
    
    def serialise_exception(self, e: Exception):
        return self._get_exception_meta(e).serialise_exception(e)

    def _get_slug_internal(self, *args: str) -> str:
        res = slugify("_".join(args), separator="_", max_length=160)
        return cast(str, res)

    def should_retry(self, e: Exception) -> bool:
        return self._get_exception_meta(e).should_retry(e)

    def recoverable(self, e: Exception) -> bool:
        return self._get_exception_meta(e).recoverable(e)

    def should_record_stack(self, e: Exception) -> bool:
        return self._get_exception_meta(e).should_record_stack(e)
