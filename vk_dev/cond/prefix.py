from vk_dev import Condition


class Prefix(Condition):
    """
    Check how message start
    """

    def __init__(self, *prefixes: str):
        self._prefixes = prefixes

    def code(self, event, pl):
        if event.object.message.text.startswith(self._prefixes):
            return True
        return False
