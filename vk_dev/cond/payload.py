from typing import Any

from vk_dev import Condition


class Payload(Condition):
    """
    Check payload params in message

    *with_value: are any keys
    with this value or not

    **kwargs: is key from kwargs
    in payload.
    If key's value is None then
    return True if key doesn't
    exist.
    If key's value is Ellipsis (...) then
    return True if key exist
    with some value.
    If key has any different value
    then check values

    Without some values in __init__
    just check is a payload in message
    or not
    """
    def __init__(self, *with_value: Any, **kwargs: dict):
        self._with_value = with_value
        self._kwargs = kwargs

    def code(self, event, pl):
        if 'payload' in event.object.message:

            payload = eval(event.object.message.payload)

            for value in self._with_value:
                if value not in payload.values():
                    return False
                    
            for key, value in self._kwargs.items():
                if value is None:
                    if key in payload:
                        return False
                elif key not in payload:
                    if value is not None:
                        return False
                else:
                    if (value is not Ellipsis) and (payload[key] != value):
                        return False

            return True

        return False
