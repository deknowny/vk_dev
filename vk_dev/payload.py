from functools import wraps
from .dot_dict import DotDict

def payload(func):
    """
    Decorator for payload functions
    """
    @wraps(func)
    def wrapper(event, *args, **kwargs):
        return DotDict(func(event=event, *args, **kwargs))

    return wrapper
