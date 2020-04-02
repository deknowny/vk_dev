import uuid
from abc import ABC, abstractmethod # , abstractproperty

class Condition(ABC):
    """
    Inheriting gives you new decorators

    ```python
    class Prefix(Condition):
        \"""
        Check msg start with prefix or don't
        \"""
        def __call__(self, *prefixes):
            self._call_switch()
            self._prefixes = prefixes

            return self

         def code(self, event, pl):
            for i in self._prefixes:
                if event.object.message.text.startwith(i):
                    return True
            return False

    prefix = Prefix()
    ```
    """

    @abstractmethod
    def code(self, event, pl):
        """
        Code that should return True/False.
        Calling with LP event and payload
        """

    def __call__(self):
        self._call_switch()

    def conf(self, id):
        """
        Escaping repetitions with
        similar decorators.
        If you want this will be the same

        ```python
        @prefix('/', '.')
        def foo(event, pl): pass

        @prefix('.', '/')
        def egg(event, pl): pass
        ```

        Use this method

        ```python
        @prefix('/', '.').conf(id='myprefs')
        def foo(event, pl): pass

        @prefix('.', '/').conf(id='myprefs')
        def egg(event, pl): pass
        ```
        """
        self.conf_id = id

    def _call_switch(self):
        """
        Cange __call__ after calling decorator.
        Use it when you create your __call__
        ```python

        def __call__(self, *prefixes):
            self._call_switch() # required
            self._prefixes = prefixes # You will use it later

            return self # required
        ```
        """
        self.__class__.__call__, self.__class__._new_call =\
        self.__class__._new_call, self.__class__.__call__

    def _new_call(self, func):
        """
        New __call__ for reaction's decorate
        """
        # self.uuid = uuid.uuid4().hex
        self.func = func
        self._call_switch()
        func.conditions.append(self)
        return func
