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
        resp = r.post(url + method, api_data).json()

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

    def __init__(
            self, auth,
            faileds=[], **kwargs
        ):
        self.auth = auth
        self.faileds = faileds
        self.start_settings = kwargs
        se;f.ractions = []

    def __getattr__(self, event_name):
        """
        Get handling event
        """
        ...

    def __call__(self, **kwargs):
        """
        Init LongPoll listening
        """
        ## Yours settings
        self.lp_settings = kwargs
        ## Intermediate lp params like server, ts and key
        self.lp_info = self.auth(self._method_name, kwargs)

        while True:
            ## Lp events
            self.lp = r.post(
                    url=server,
                    data={**lp_info, **kwargs}
                )
            self._failed_handler()
            ## Reaction



    def _failed_handler(self):
        """
        Catch lp faileds
        """
        if 'failed' in self.lp:
            if self.lp['failed'] in self.faileds:
                self._failed_resolving()

            else:
                raise VkErr(str(self.lp))

        else:
            self.lp_info['ts'] = self.lp['ts']

    def _failed_resolving(self):
        """
        Resolve faileds problems
        """
        if self.lp['failed'] == 1:
            self.lp_info['ts'] = self.lp['ts']

        elif self.lp['failed'] in (2, 3):
            self.lp_info = self.auth(
                    self._method_name,
                    kwargs
                )

        elif self.lp['failed'] == 4:
            self.lp_settings['version'] = self.lp['max_version']



    def _method_name(self):
        """
        Choose method for users and groups
        """
        if self.auth.type == 'group':
            return 'groups.getLongPollServer'
        else:
            return 'messages.getLongPollServer'
