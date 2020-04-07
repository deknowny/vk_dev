from vk_dev import Condition


class Prefix(Condition):
    """
    Check how message start
    *prefixes: str
    """

    def __init__(self, *prefixes):
        self._prefixes = prefixes

    def code(self, event, pl):
        return event.object.message.text.startswith(self._prefixes)
