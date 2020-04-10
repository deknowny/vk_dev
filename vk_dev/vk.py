import time
import json
import sys
import asyncio
import ssl
import inspect
from typing import Union, Any, NoReturn, Optional
from datetime import datetime as dt

from .exception import VkErr
from .tools import peer
from .dot_dict import DotDict

import aiohttp
import requests


def no_api_wrapper(cls):
    """
    For NoApi only
    """
    return cls()

class _Api:
    """
    For async and not API classes
    """
    def _error_check(self, resp: dict) -> Union[DotDict, Any]:
        if 'error' in resp:
            raise VkErr(resp)
        else:
            if isinstance(resp['response'], dict):
                return DotDict(resp['response'])
            return resp['response']

    @property
    def method(self) -> None:
        """
        Method name
        """
    @method.getter
    def method(self) -> str:
        res = self._method
        self._method = None
        return res

    @method.setter
    def method(self, value: str) -> None:
        if self._method is None:
            self._method = value
        else:
            self._method += '.' + value

@no_api_wrapper
class NoApi(_Api):
    """
    API requests without async
    """
    def __init__(self) -> None:
        self._method = None

    def __rrshift__(self, api: "Api") -> Union[DotDict, Any]:
        self.api_data.update(
            {
            'access_token': api.token,
            'v': api.v
            }
        )
        r = requests.post(api.url + self.method, data=self.api_data)
        resp = r.json()
        return self._error_check(resp)


    def __call__(self, **data) -> "NoApi":
        self.api_data = data
        return self

    def __getattr__(self, value: str) -> "NoApi":
        self.method = value
        return self

    def _request_wait(self) -> None:
        """
        Pause between requests
        """
        now = time.time()
        diff = now - self._last_request_time

        if diff < self._freeze_time:
            time.sleep(self._freeze_time - diff)
            self._last_request_time = time.time()

class Api(_Api):
    """
    Make async API requests and
    API-helpers handler.

    Contain main info like
    access_token,
    version and etc.
    """
    def __init__(
            self,
            token: str,
            v: Union[str, float],
            group_id: int = 0
        ) -> None:
        self.url = 'https://api.vk.com/method/'
        self.token = token
        self.v = str(v)
        self.group_id = abs(group_id)
        self.type = 'group' if self.group_id else 'user'
        self.session = aiohttp.ClientSession()
        self.ssl = ssl.SSLContext()
        self._last_request_time = time.time()
        self._freeze_time = 1 / 3 if self.type == 'user' else 1 / 20
        self._method = None

    def __getattr__(self, value: str) -> "Api":
        self.method = value
        return self

    async def __call__(self, **kwargs) -> DotDict:
        """
        Make every API requests
        """
        return await self.request(self.method, data=kwargs)

    async def request(self, method: str, data: dict) -> DotDict:
        """
        Make every API requests
        """
        api_data = {
            'access_token': self.token,
            'v': self.v,
            **data
        }

        await self._request_wait()

        async with self.session.post(self.url + method, data=api_data, ssl=self.ssl) as r:
            resp = await r.json()

        return self._error_check(resp)

    async def _request_wait(self) -> None:
        """
        Pause between requests
        """
        now = time.time()
        diff = now - self._last_request_time

        if diff < self._freeze_time:
            await asyncio.sleep(self._freeze_time - diff)
            self._last_request_time = time.time()


class LongPoll:
    """
    LongPoll scheme
    """
    user_get = {
        'need_pts': False,
        'lp_version': 3
    }
    user_init = {
        'wait': 25,
        'mode': 234,
        'version': 10
    }
    group_get = {
        # group_id
    }
    group_init = {
        'wait': 25
    }

    def __init__(self, faileds=[], default=True, **kwargs) -> None:
        self.faileds = faileds
        self.start_settings = kwargs
        self.reaction_handlers = []

    def __rrshift__(self, api):
        self.api = api
        return self

    def __getattr__(self, event_name: str) -> "ReactionHandler":
        """
        Get handling event
        """
        hand = ReactionHandler(event_name)
        self.reaction_handlers.append(hand)

        return hand

    async def _lp_start(self, default=True, **kwargs) -> NoReturn:

        ## Reactions tree
        self._reactions_init()

        if self.api.type == 'group':
            LongPoll.group_get['group_id'] = self.api.group_id

        self.start_settings = {
                **((LongPoll.user_get if self.api.type == 'user' else LongPoll.group_get) if default else {}),
                **self.start_settings
            }

        ## Yours settings
        self.lp_settings = {**(LongPoll.group_init if self.api.type == 'group' else LongPoll.group_get), **kwargs} if default else kwargs

        ## Intermediate lp params like server, ts and key
        self.lp_info = await self.api.request(
                method=self._method_name(),
                data=self.start_settings
            )
        self.start_time = dt.now()
        self.format_start = self.start_time.strftime("[%Y-%m-%d %H:%M:%S]")
        print(f"\033[2m{self.format_start} \033[0m\033[32mListening VK LongPoll...\033[0m")

        ## Stats
        self.events_get = 0
        self.events_handled = 0


        while True:
            ## Lp events

            lp_get = {
                'key': self.lp_info['key'],
                'ts': self.lp_info['ts']
            }

            data = {**lp_get, **self.lp_settings, 'act': 'a_check'}

            async with self.api.session.post(self.lp_info['server'], data=data, ssl=self.api.ssl) as response:
                self.lp = await response.json()

            res = self._failed_handler()
            if res is True:
                continue

            for update in self.lp['updates']:
                event = DotDict(update)
                self.events_get += 1
                if event.type in self.reactions:
                    self.events_handled += 1
                    self.loop.create_task(self._reactions_get(event))
                    # self.loop.create_task(self._reactions_call())

    def __call__(self, default=True, **kwargs) -> NoReturn:
        """
        Init LongPoll listening
        """
        try:
            loop = asyncio.get_event_loop()
            self.loop = loop
            loop.create_task(self._lp_start(default, **kwargs))
            loop.run_forever()

        except KeyboardInterrupt:
            end_time = dt.now()
            dif = end_time - self.start_time
            format_end = end_time.strftime("[%Y-%m-%d %H:%M:%S]")

            print(f"\n\033[2m{format_end} \033[0m\033[33mListening has been stoped\033[0m")
            print("Handled \033[36m%s\033[0m (\033[35m%.2f ps\033[0m)" % (
                self.events_handled,
                self.events_handled / dif.seconds
            ))
            print("Total \033[36m%s\033[0m (\033[35m%.2f ps\033[0m)" % (
                self.events_get,
                self.events_get / dif.seconds
            ))
            print(f"Taken \033[36m{dif}\033[0m")
            exit()

    async def _reactions_call(self, event, reaction) -> None:
        """
        Call every reaction
        """
        if reaction.pl_gen is None:
            payload = None
        elif inspect.iscoroutinefunction(reaction.pl_gen):
            payload = await reaction.pl_gen(event)
        else:
            payload = reaction.pl_gen(event)

        for cond in reaction.conditions:
            if inspect.iscoroutinefunction(cond.code):
                res = await cond.code(event, payload)
                if not res:
                    break
            else:
                if not cond.code(event, payload):
                    break
        else:
            if inspect.iscoroutinefunction(reaction):
                self.loop.create_task(reaction(event, payload))

            else:
                reaction(event, payload)


    async def _reactions_get(self, event) -> None:
        """
        Return list of needed funcs with payload
        """
        for reaction in self.reactions[event.type]:
            self.loop.create_task(self._reactions_call(event, reaction))


    def _reactions_init(self) -> None:
        """
        Init reactions tree
        """
        reactions = {}

        for handler in self.reaction_handlers:
            if handler.event_name not in reactions:
                reactions[handler.event_name] = [handler.reaction]
            else:
                reactions[handler.event_name].append(handler.reaction)

        self.reactions = reactions

    def _failed_handler(self) -> Union[bool, None]:
        """
        Catch lp faileds
        """
        if 'failed' in self.lp:

            if self.lp['failed'] in self.faileds:
                self._failed_resolving()
                return True

            else:
                raise VkErr(self.lp)

        else:
            self.lp_info['ts'] = self.lp['ts']

    def _failed_resolving(self) -> None:
        """
        Resolve faileds problems
        """
        if self.lp['failed'] == 1:
            self.lp_info['ts'] = self.lp['ts']

        elif self.lp['failed'] in (2, 3):
            self.lp_info = self.auth(
                    self._method_name(),
                    self.start_settings
                )

        elif self.lp['failed'] == 4:
            self.lp_settings['version'] = self.lp['max_version']

    def _method_name(self) -> None:
        """
        Choose method for users and groups
        """
        if self.api.type == 'group':
            return 'groups.getLongPollServer'
        else:
            return 'messages.getLongPollServer'


class ReactionHandler:
    """
    Reactions Handler
    """
    def __init__(self, event_name) -> None:
        self.event_name = event_name

    def __call__(self, pl_gen=None):
        """
        Take payload generator
        """
        self.pl_gen = pl_gen

        self.__class__.__call__, self.__class__._reaction_decor =\
        self.__class__._reaction_decor, self.__class__.__call__

        return self

    def _reaction_decor(self, func: Any) -> Any:
        """
        Called when it is decorating
        """
        self.__class__.__call__, self.__class__._reaction_decor =\
        self.__class__._reaction_decor, self.__class__.__call__
        self.reaction = func

        func.event_name = self.event_name
        func.conditions = []
        func.pl_gen = self.pl_gen

        return func

class Keyboard:
    """
    Create VK Keyboard by dict or buttons list
    """
    def __init__(self, kb: Optional[dict] = None, **kwargs) -> None:
        if kb is None:
            self.kb = {
                **kwargs,
                'buttons': [[]]
            }
        else:
            self.kb = kb

    def __add__(self, button) -> None:
        """
        Add button to line
        """

        self.kb['buttons'][-1].append(button())

    def __repr__(self) -> str:
        """
        Create for sending
        """
        kb = json.dumps(self.kb, ensure_ascii=False)
        kb = kb.encode('utf-8').decode('utf-8')
        return str(kb)

    def create(self, *buttons) -> "Keyboard":
        """
        Create keyboard by Buttons object
        """
        for button in buttons:
            if not isinstance(button, Button):
                raise TypeError(f"Keyboard's buttons must be 'Button' instance, not '{type(button).__name__}'")

            if button.info is None:
                self.kb['buttons'].append([])
            else:
                self.kb['buttons'][-1].append(button.info)

        return self


class Button:
    """
    Keyboard button
    """
    def __init__(self, **kwargs) -> None:
        self.info = {'action': {**kwargs}}

    def positive(self) -> "Button":
        """
        Green button
        """
        self.info['color'] = 'positive'
        return self

    def negative(self) -> "Button":
        """
        Red button
        """
        self.info['color'] = 'negative'
        return self

    def secondary(self) -> "Button":
        """
        White button
        """
        self.info['color'] = 'secondary'
        return self

    def primary(self) -> "Button":
        """
        Blue button
        """
        self.info['color'] = 'primary'
        return self

    @classmethod
    def _button_init(cls, **kwargs) -> "Button":
        self = super().__new__(cls)
        self.__init__(**kwargs)

        return self

    @classmethod
    def line(cls) -> "Button":
        """
        Add Buttons line
        """
        self = cls._button_init()
        self.info = None

        return self

    @classmethod
    def text(cls, **kwargs) -> "Button":
        return cls._button_init(type='text', **kwargs)

    @classmethod
    def open_link(cls, **kwargs) -> "Button":
        return cls._button_init(type='open_link', **kwargs)

    @classmethod
    def location(cls, **kwargs) -> "Button":
        return cls._button_init(type='location', **kwargs)

    @classmethod
    def vkpay(cls, **kwargs) -> "Button":
        return cls._button_init(type='vkpay', **kwargs)

    @classmethod
    def open_app(cls, **kwargs) -> "Button":
        return cls._button_init(type='open_app', **kwargs)
