# -*- coding: utf-8 -*-
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

from .wiki import MediaWiki


def blocking(call):
    """Turns a async callable into a blocking one.

    :param call: An async callable.
    """

    def block_call(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(call(*args, **kwargs))

    return block_call


class BlockingMeta(type):
    """Metaclass to turn coroutines into blocking methods.
    """

    def __new__(cls, name, base, attrs):
        new_cls = super().__new__(cls, name, base, attrs)

        no_synchronize = ['request2api']
        for attr_name in dir(new_cls):
            attr = getattr(new_cls, attr_name)
            if attr_name not in no_synchronize and asyncio.iscoroutinefunction(
                    attr):
                setattr(new_cls, attr_name, blocking(attr))
        return new_cls


class BlockingMediaWiki(MediaWiki, metaclass=BlockingMeta):
    pass
