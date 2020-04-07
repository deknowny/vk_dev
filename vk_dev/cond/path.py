from vk_dev import Condition


class Path(Condition):
    """
    Message's path
    path: Enum[str] = [
        'chat',
        'direct'
    ]
    """

    def __init__(self, path):
        self._path = path

    def code(self, event, pl):
        if event.object.message.peer_id < 2000000000:
            return 'direct' == self._path
        return 'chat' == self._path
