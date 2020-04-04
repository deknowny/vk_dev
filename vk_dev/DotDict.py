class DotDict(dict):
    """
    Wrapper for dictioanries for calling elements by dot,
    also work like ordinary dict.
    Work correctly if all elements are primitives
    """

    def __init__(self, d):
        super().__init__(d)

    def __getattr__(self, value):
        """
        Congested for dot-syntax
        """
        return self._get_value(self[value])

    def _get_value(self, value):
        """
        Return dict that wrapped in DotDict
        """

        if isinstance(value, dict):
            return self.__class__(value)

        elif isinstance(value, list):
            return [self._get_value(i) for i in value]

        return value
