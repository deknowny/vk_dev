import asyncio
import time
import json

import aiohttp

from .exception import VkErr
from .dot_dict import DotDict


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
        self.url = "https://api.vk.com/method/"
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession()
        self.token = token
        self.v = str(v)
        self.group_id = abs(group_id)
        self.type = "group" if self.group_id else "user"
        self._last_request_time = time.time()
        self._freeze_time = 1 / 3 if self.type == "user" else 1 / 20

    async def __call__(self, method, data):
        """
        Make every API requests
        """
        api_data = {"access_token": self.token, "v": self.v, **data}
        await self._request_wait()

        async with self.session.post(self.url + method, data=api_data) as r:
            resp = await r.json()

        if "error" in resp:
            raise VkErr(resp)

        if isinstance(resp["response"], dict):
            return DotDict(resp["response"])
        return resp["response"]

    async def _request_wait(self):
        """
        Pause between requests
        """
        now = time.time()
        diff = now - self._last_request_time

        if diff < self._freeze_time:
            await asyncio.sleep(self._freeze_time - diff)
            self._last_request_time = now + self._freeze_time


class Api:
    """
    For API requests by dot-syntax
    """

    def __init__(self, auth: Auth):
        self.auth = auth
        self._method = None

    @property
    def method(self):
        res = self._method
        self._method = None
        return res

    @method.setter
    def method(self, value):
        if self._method is None:
            self._method = value
        else:
            self._method += "." + value

    def __getattr__(self, value):
        self.method = value
        return self

    async def __call__(self, **kwargs):
        """
        Make request
        """
        return await self.auth(self.method, kwargs)


class Handler:
    """
    Handler useful often used
    API requests schemes, like
    LongPoll, quickly photo uploading and etc.
    """

    def __init__(self, auth):
        self.auth = auth

    def longpoll(self, default=True, failed=None, **kwargs):
        """
        Init LongPoll
        """
        if failed is None:
            failed = []
        if self.auth.type == "group":
            LongPoll.group_get["group_id"] = self.auth.group_id
        return LongPoll(
            self.auth,
            faileds=failed,
            **{
                **(
                    (
                        LongPoll.user_get
                        if self.auth.type == "user"
                        else LongPoll.group_get
                    )
                    if default
                    else {}
                ),
                **kwargs,
            }
        )

    @staticmethod
    def keyboard(kb):
        return Keyboard(kb)


class LongPoll:
    """
    LongPoll scheme
    """

    user_get = {"need_pts": False, "lp_version": 3}
    user_init = {"wait": 25, "mode": 234, "version": 10}
    group_get = {
        # group_id
    }
    group_init = {"wait": 25}

    def __init__(self, auth: Auth, failed=None, **kwargs):
        if failed is None:
            failed = []
        self.auth = auth
        self.failed = failed
        self.start_settings = kwargs
        self.reaction_handlers = []

    def __getattr__(self, event_name):
        """
        Get handling event
        """
        hand = ReactionHandler(event_name)
        self.reaction_handlers.append(hand)

        return hand

    async def __start_lp(self, default=True, **kwargs):
        # Reactions tree
        self._reactions_init()
        # Yours settings
        self.lp_settings = (
            {
                **(
                    LongPoll.group_init
                    if self.auth.type == "group"
                    else LongPoll.group_get
                ),
                **kwargs,
            }
            if default
            else kwargs
        )
        # Intermediate lp params like server, ts and key

        self.lp_info = await self.auth(self._method_name(), self.start_settings)
        print("""\033[32mListening VK LongPoll...\033[0m""")

        while True:
            # Lp events
            lp_get = {"key": self.lp_info["key"], "ts": self.lp_info["ts"]}

            async with self.auth.session.post(
                    url=self.lp_info["server"],
                    data={**lp_get, **self.lp_settings, "act": "a_check"},
            ) as r:
                self.lp = await r.json()

            res = await self._failed_handler()
            if res:
                continue

            for update in self.lp["updates"]:
                self.event = DotDict(update)
                if self.event.type in self.reactions:
                    self._reactions_get()
                    await self._reactions_call()

    def __call__(self, default=True, **kwargs):
        """
        Init LongPoll listening
        """
        loop = asyncio.get_event_loop()
        self.loop = loop
        loop.create_task(self.__start_lp(default, **kwargs))
        loop.run_forever()

    async def _reactions_call(self):
        """
        Call every reaction
        """
        for reaction, payload in self.results:
            self.loop.create_task(reaction(self.event, payload))

    def _reactions_get(self):
        """
        Return list of needed funcs with payload
        """
        self.results = []
        for reaction in self.reactions[self.event.type]:
            payload = (
                reaction.pl_gen(self.event) if reaction.pl_gen is not None else None
            )
            for cond in reaction.conditions:
                if not cond.code(self.event, payload):
                    break
            else:
                self.results.append((reaction, payload))

    def _reactions_init(self):
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

    async def _failed_handler(self):
        """
        Catch lp faileds
        """
        if "failed" in self.lp:
            if self.lp["failed"] in self.faileds:
                await self._failed_resolving()
                return True
            raise VkErr(str(self.lp))
        self.lp_info["ts"] = self.lp["ts"]

    async def _failed_resolving(self):
        """
        Resolve faileds problems
        """
        if self.lp["failed"] == 1:
            self.lp_info["ts"] = self.lp["ts"]

        elif self.lp["failed"] in (2, 3):
            self.lp_info = await self.auth(self._method_name(), self.start_settings)

        elif self.lp["failed"] == 4:
            self.lp_settings["version"] = self.lp["max_version"]

    def _method_name(self):
        """
        Choose method for users and groups
        """
        if self.auth.type == "group":
            return "groups.getLongPollServer"
        return "messages.getLongPollServer"


class ReactionHandler:
    """
    Reactions Handler
    """

    def __init__(self, event_name):
        self.event_name = event_name

    def __call__(self, pl_gen=None):
        self.pl_gen = pl_gen

        self.__class__.__call__, self.__class__._reaction_decor = (
            self.__class__._reaction_decor,
            self.__class__.__call__,
        )

        return self

    def _reaction_decor(self, func):
        """
        Called when it is decorating
        """

        self.__class__.__call__, self.__class__._reaction_decor = (
            self.__class__._reaction_decor,
            self.__class__.__call__,
        )
        self.reaction = func

        func.event_name = self.event_name
        func.conditions = []
        func.pl_gen = self.pl_gen

        return func


class Keyboard:
    """
    Create VK Keyboard by dict
    """

    def __init__(self, kb=None):
        if kb is None:
            kb = {}
        self.kb = kb

    def __repr__(self):
        kb = json.dumps(self.kb, ensure_ascii=False)
        kb = kb.encode("utf-8").decode("utf-8")
        return str(kb)
