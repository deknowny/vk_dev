from functools import wraps
import inspect

from .dot_dict import DotDict


def payload(func):
    """
    Decorator for payload functions
    """
    if inspect.iscoroutinefunction(func):
        async def wrapper(event, *args, **kwargs):
            res = await func(event=event, *args, **kwargs)
            return DotDict(res)
    else:
        def wrapper(event, *args, **kwargs):
            return DotDict(func(event=event, *args, **kwargs))

    wrapper = wraps(func)(wrapper)

    return wrapper
