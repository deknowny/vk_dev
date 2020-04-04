from vk_dev import Condition, peer

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
        if event.object.message.peer_id < peer:
            return 'direct' == self._path
        else:
            return 'chat' == self._path
