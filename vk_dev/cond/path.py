from typing import Literal

from vk_dev import Condition, peer


class Path(Condition):
    """
    Message's path
    """

    def __init__(self, path: Literal['chat', 'direct']):
        self._path = path

    def code(self, event, pl):
        if event.object.message.peer_id > peer:
            return 'direct' == self._path
        return 'chat' == self._path
