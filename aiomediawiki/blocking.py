# -*- coding: utf-8 -*-
"""This module implements a blocking interface to mediawiki mainly
for use in the python shell.
"""
# Copyright 2020 Juca Crispim <juca@poraodojuca.net>

# This file is part of aiomediawiki.

# aiomediawiki is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# aiomediawiki is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with aiomediawiki. If not, see <http://www.gnu.org/licenses/>.

import asyncio

from .page import MediaWikiPage
from .wiki import MediaWiki


def blocking(call):
    """Turns a async callable into a blocking one.

    :param call: An async callable.
    """

    def block_call(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(call(*args, **kwargs))

    block_call.__original__ = call

    return block_call


class BlockingMeta(type):
    """Metaclass to turn coroutines into blocking methods.
    """

    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)

        no_synchronize = attrs.get('no_synchronize', [])
        for attr_name in dir(new_cls):
            attr = getattr(new_cls, attr_name)
            should_block = (not attr_name.startswith('_') and
                            attr_name not in no_synchronize)
            if should_block and asyncio.iscoroutinefunction(
                    attr):
                setattr(new_cls, attr_name, blocking(attr))
        return new_cls


class BlockingSearchResults(list):
    """Blocking container for mediawiki results.
    """

    def load_all(self):
        """Synchronous version of load_all. Note that the pages
        are loaded concurrently.
        """
        futs = [p.load.__original__(p) for p in self]
        blocking(asyncio.gather)(*futs)


class BlockingMediaWikiPage(MediaWikiPage, metaclass=BlockingMeta):
    """A MediaWikiPage that blocks when loading"""


class BlockingMediaWiki(MediaWiki, metaclass=BlockingMeta):
    """A MediaWiki that has blocking io operations."""

    PAGE_CLS = BlockingMediaWikiPage
    SEARCH_RESULTS_CLS = BlockingSearchResults

    no_synchronize = [
        'request2api'
    ]

    async def _load_page(self, page):
        return await page.load.__original__(page)
