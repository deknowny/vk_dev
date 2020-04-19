from __future__ import annotations
import json
from textwrap import dedent
from typing import (
    Optional,
    Union,
    Generator, AsyncGenerator
)


class Button:
    """
    Keyboard button
    """
    def __init__(self, **kwargs) -> None:
        self.info = {'action': {**kwargs}}

    def positive(self) -> Button:
        """
        Green button
        """
        self.info['color'] = 'positive'
        return self

    def negative(self) -> Button:
        """
        Red button
        """
        self.info['color'] = 'negative'
        return self

    def secondary(self) -> Button:
        """
        White button
        """
        self.info['color'] = 'secondary'
        return self

    def primary(self) -> Button:
        """
        Blue button
        """
        self.info['color'] = 'primary'
        return self

    @classmethod
    def _button_init(cls, **kwargs) -> Button:
        self = super().__new__(cls)
        if 'payload' in kwargs:
            kwargs['payload'] = str(kwargs['payload']).replace('\'', '"')
        self.__init__(**kwargs)

        return self

    @classmethod
    def line(cls) -> Button:
        """
        Add Buttons line
        """
        self = cls._button_init()
        self.info = None

        return self

    @classmethod
    def text(cls, **kwargs) -> Button:
        return cls._button_init(type='text', **kwargs)

    @classmethod
    def open_link(cls, **kwargs) -> Button:
        return cls._button_init(type='open_link', **kwargs)

    @classmethod
    def location(cls, **kwargs) -> Button:
        return cls._button_init(type='location', **kwargs)

    @classmethod
    def vkpay(cls, **kwargs) -> Button:
        return cls._button_init(type='vkpay', **kwargs)

    @classmethod
    def open_app(cls, **kwargs) -> Button:
        return cls._button_init(type='open_app', **kwargs)


class Keyboard:
    """
    messages.send: keyboard
    Create VK Keyboard by dict or buttons list
    """
    def __init__(self, kb: Optional[dict] = None, **kwargs) -> None:
        if kb is None:
            self.kb = {
                **kwargs,
                'buttons': [[]]
            } if kwargs else []
        else:
            self.kb = kb

        # Check last for template or not
        self._kwargs = kwargs

    def __add__(self, button: Button) -> None:
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

    def create(self, *buttons: Button) -> Keyboard:
        """
        Create keyboard by Buttons object
        """
        for button in buttons:
            if not isinstance(button, Button):
                error_msg = "Keyboard's buttons must be 'Button' instance, not"
                raise TypeError(
                    dedent(f"""
                        {error_msg} '{type(button).__name__}'
                    """)
                )
            if button.info is None:
                self.kb['buttons'].append([])
            else:
                if self._kwargs:
                    self.kb['buttons'][-1].append(button.info)
                else:
                    self.kb.append(button.info)

        return self


class Element:
    """
    Element for carousel
    """
    def __init__(self, **kwargs) -> None:
        self.info = kwargs
        self.info['action'] = {}

    def open_link(self, link: str) -> "Element":
        self.info['action']['type'] = 'open_link'
        self.info['action']['link'] = link
        return self

    def open_photo(self) -> "Element":
        self.info['action']['type'] = 'open_photo'
        return self


class Template:
    """
    messages.send: template
    For example, you can
    create carousel with this
    """
    def __init__(self, tp: Optional[dict] = None) -> None:
        """
        Init by dict described by vk scheme.
        Also you can use generators for this,
        just decorate your generator
        with Template's object
        """
        if tp is None:
            self.tp = {
                'type': 'carousel',
                'elements': []
            }
        else:
            self.tp = tp

    def __call__(
            self,
            gen: Union[
                Generator[Element, None, None],
                AsyncGenerator[Element, None]
            ]
        ) -> None:
        """
        Create carousel with
        decorating generatore
        """
        for elem in gen():
            elem.info['buttons'] = elem.info['buttons'].kb
            self.tp['elements'].append(elem.info)

    def __repr__(self) -> str:
        tp = json.dumps(self.tp, ensure_ascii=False)
        tp = tp.encode('utf-8').decode('utf-8')
        return str(tp)
