from __future__ import annotations
import ssl
import os
from typing import (
    Optional,
    IO, Any
)

import aiohttp

from .dot_dict import DotDict


class DocInfo:
    def __init__(self, response: dict) -> None:
        self.type = response['type']
        self.info = DotDict(response[self.type])

    def __repr__(self) -> str:
        return f"doc{self.info.owner_id}_{self.info.id}"


class Document:
    """
    Quick send and work with documents
    """
    def __rrshift__(self, api) -> Document:
        self.api = api
        return self

    @classmethod
    def to_message(cls, **kwargs) -> Document:
        """
        Documents fos messages
        """
        self = cls()
        self._method = 'docs.getMessagesUploadServer'
        self._params = kwargs
        return self

    @classmethod
    def to_wall_and_message(cls, **kwargs) -> Document:
        """
        Documents for walls and messages
        """
        self = cls()
        self._method = 'docs.getWallUploadServer'
        self._params = kwargs
        return self

    async def load(
            self, *,
            file: Optional[IO[Any]] = None,
            title: Optional[str] = None,
            tags: Optional[str] = None,
            return_tags: Optional[bool] = None
        ) -> DocInfo:
        """
        Load doc to vk.
        Params will be passed to `docs.save` method.

        """
        if title is None:
            title = os.path.basename(file.name)

        url = await self.api.request(self._method, self._params)
        url = url['upload_url']

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data={
                    "file": file
                },
                ssl=ssl.SSLContext()
            ) as r:
                file_info = await r.json()

        if 'error' in file_info:
            raise ValueError(
                f"Something wrong with your file\n{file_info}"
            )

        file_info = await self.api.docs.save(
            file=file_info['file'],
            title=title,
            tags=tags,
            return_tags=return_tags
        )

        return DocInfo(file_info)
