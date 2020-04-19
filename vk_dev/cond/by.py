from typing import Literal

from vk_dev import Condition


class By(Condition):
    """
    Check, who wrote a message: group or user
    """
    def __init__(self, writer: Literal['user', 'group']):
        self._writer_type = writer_type

    def code(self, event):
        if event.object.message.from_id > 0:
            return 'user' == self._writer_type
        return 'group' == self._writer_type
