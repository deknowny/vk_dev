import uuid
from typing import Callable, Awaitable, Union
from abc import ABC, abstractmethod


class Condition(ABC):
    """
    Inheriting gives you new decorators
    """
    def __call__(self, func) -> Union[Callable[[str, str], None], Callable[[str, str], Awaitable[None]]]:
        self.uuid = uuid.uuid4().hex
        self.func = func
        func.conditions.append(self)
        if not hasattr(self, 'conf_id'):
            self.conf_id = self.uuid

        return func

    @abstractmethod
    def code(self, event, pl) -> bool:
        """
        Code that should return True/False.
        Calling with LP event and payload.
        ```python
        def code(self, event, pl):
            if event.object.message.text.startswith(self._prefixes):
                return True
            return False
        ```
        """
