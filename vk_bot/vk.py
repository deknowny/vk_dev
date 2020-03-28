from exception import VkErr
from tools import url, peer
from DotDict import DotDict

import time

import requests



class Auth:
    """
    Auth to vk by token.
    Both for users and gropus
    """

    def __new__(cls, **kwargs):
        """
        Return a tuple of API handlers
        """
        self = super().__new__(cls)
        self.__init__(**kwargs)

        return Api(self), Handler(self)


    def __init__(self, token, v, group_id=0):
        self.token = token
        self.v = str(v)
        self.group_id = abs(group_id)
        self.type = self._type()
        self._last_request = time()

    def __call__(self, method, data):
        """
        Make every API requests
        """
        api_data = {
            'access_token': self.token,
            'v': self.v,
            **data
        }
        self._request_wait()
        resp = r.post(url + method, data=api_data).json()

        if 'error' in resp:
            raise VkErr(resp)

        else:
            if type(resp['response']) == dict:
                return DotDict(resp['response'])

            else:
                return resp['response']

    def _request_wait(self):
        """
        Pause between requests
        """
        freeze_time = 0.334
        now = time()
        diff = now - self._last_request

        if diff < freeze_time:
            time.sleep(freeze_time - diff)
            self._last_request = now + freeze_time

    def _type(self):
        if group_id:
            return 'group'
        else:
            return 'user'


class Api:
    """
    For API requests by dot-syntax
    """
    def __init__(self, auth):
        self.auth = auth

    def __getattr__(self, value):
        if self.method is None:
            self.method = value

        else:
            self.method += '.' + value

    def __call__(self, **kwargs):
        """
        Make request
        """
        return self.api(self.method, kwargs)


class Handler:
    """
    Handler usefull often used
    API requests schemes, like
    LongPoll, quickly photo uploading and etc.
    """
    def __init__(token, auth):
        self.auth = auth

    # def LongPoll(
    #     self,
    #     wait=25,
    #     v=3,
    #     mode=2,
    #     handle_faileds=[]
    #     ):
    #     return LongPoll(auth, wait=25,)


class LongPoll:
    """
    LongPoll scheme
    """
    def __getattr__(self, event_name):
        """
        Get handling event
        """
        def cond(func):
            """
            Function-decorator for reaction function
            """
            def wrapper(event, pl):
                """
                New function with type event checking
                """
                if ... == event_name: # idk
                    func()

            wrapper.event = func.event
            wrapper.pl = func.pl

            return wrapper

        return cond

        ## So hard make this
