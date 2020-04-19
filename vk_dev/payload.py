from functools import wraps
from typing import Callable, Awaitable, Union
import inspect

from .dot_dict import DotDict


def payload(func) -> Union[Callable[..., DotDict], Callable[..., Awaitable[DotDict]]]:
    """
    Decorator for payload functions
    """
    if inspect.iscoroutinefunction(func):
        async def wrapper(event: str, *args, **kwargs) -> DotDict:
            res = await func(event=event, *args, **kwargs)
            return DotDict(res)
    else:
        def wrapper(event: str, *args, **kwargs) -> DotDict:
            return DotDict(func(event=event, *args, **kwargs))

    wrapper = wraps(func)(wrapper)

    return wrapper
