from __future__ import annotations
import time
import asyncio
import ssl
import inspect
from datetime import datetime as dt
from typing import (
    Union, Any,
    NoReturn
)

import aiohttp

from .exception import VkErr
from .dot_dict import DotDict




class Api:
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
        self.ssl = ssl.SSLContext()
        self._last_request_time = time.time()
        self._freeze_time = 1 / 3 if self.type == 'user' else 1 / 20
        self._method = None

    def __getattr__(self, value: str) -> Api:
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

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url + method, data=api_data, ssl=self.ssl
            ) as r:
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

    def _error_check(self, resp: dict) -> Union[DotDict, Any]:
        """
        Check errors from response
        """
        if 'error' in resp:
            raise VkErr(VkErr.text_init(resp))
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

    def __init__(self, faileds=[1, 2, 3, 4], default=True, **kwargs) -> None:
        self.faileds = faileds
        self.start_settings = kwargs
        self.reaction_handlers = []

    def __rrshift__(self, api):
        """
        Use to add your API configuration to LP
        """
        self.api = api
        return self

    def __getattr__(self, event_name: str) -> _ReactionHandler:
        """
        Get handling event
        """
        hand = _ReactionHandler(event_name)
        self.reaction_handlers.append(hand)

        return hand

    async def _lp_start(self, default=True, **kwargs) -> NoReturn:

        # Reactions tree
        self._reactions_init()

        if self.api.type == 'group':
            LongPoll.group_get['group_id'] = self.api.group_id

        self.start_settings = {
                **(
                    (
                        LongPoll.user_get
                        if self.api.type == 'user'
                        else LongPoll.group_get
                    ) if default else {}
                ),
                **self.start_settings
            }

        # Yours settings
        self.lp_settings = {
            **(
                LongPoll.group_init
                if self.api.type == 'group'
                else LongPoll.group_get
            ),
            **kwargs
        } if default else kwargs

        # Intermediate lp params like server, ts and key
        self.lp_info = await self.api.request(
                method=self._method_name(),
                data=self.start_settings
            )
        self.start_time = dt.now()
        self.format_start = self.start_time.strftime("[%Y-%m-%d %H:%M:%S]")
        listening_string = "\033[0m\033[32mListening VK LongPoll...\033[0m"
        print(f"\033[2m{self.format_start} {listening_string}")

        # Stats
        self.events_get = 0
        self.events_handled = 0

        while True:
            # Lp events
            lp_get = {
                'key': self.lp_info['key'],
                'ts': self.lp_info['ts']
            }

            data = {**lp_get, **self.lp_settings, 'act': 'a_check'}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.lp_info['server'],
                    data=data,
                    ssl=self.api.ssl
                ) as response:
                    self.lp = await response.json()

            res = await self._failed_handler()
            if res is True:
                continue

            for update in self.lp['updates']:
                event = DotDict(update)
                self.events_get += 1
                if event.type in self.reactions:
                    self.events_handled += 1
                    asyncio.create_task(self._reactions_get(event))

    def __call__(self, default=True, **kwargs) -> NoReturn:
        """
        Init LongPoll listening
        """
        try:
            # Infinity corutine
            asyncio.run(self._lp_start(default, **kwargs))

        except KeyboardInterrupt:
            end_time = dt.now()
            dif = end_time - self.start_time
            format_end = end_time.strftime("[%Y-%m-%d %H:%M:%S]")

            listening_stop = "\033[0m\033[33mListening has been stoped\033[0m"
            print(f"\n\033[2m{format_end} {listening_stop}")
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
        payload = DotDict({})
        for pl_gen in reaction.pl_gen:
            if inspect.iscoroutinefunction(pl_gen):
                res = await pl_gen(event)
                payload = DotDict({**payload, **res})
            else:
                payload = DotDict({**payload, **pl_gen(event)})

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
                asyncio.create_task(reaction(event, payload))
            else:
                reaction(event, payload)

    async def _reactions_get(self, event) -> None:
        """
        Return list of needed funcs with payload
        """
        for reaction in self.reactions[event.type]:
            asyncio.create_task(self._reactions_call(event, reaction))

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

    async def _failed_handler(self) -> Union[bool, None]:
        """
        Catch lp faileds
        """
        if 'failed' in self.lp:
            if self.lp['failed'] in self.faileds:
                await self._failed_resolving()
                return True
            else:
                raise VkErr(VkErr.text_init(self.lp))
        else:
            self.lp_info['ts'] = self.lp['ts']

    async def _failed_resolving(self) -> None:
        """
        Resolve faileds problems
        """
        if self.lp['failed'] == 1:
            self.lp_info['ts'] = self.lp['ts']
        elif self.lp['failed'] in (2, 3):
            self.lp_info = await self.api.request(
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


class _ReactionHandler:
    """
    Reactions Handler
    """
    def __init__(self, event_name: str) -> None:
        self.event_name = event_name

    def __call__(self, *pl_gen):
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
