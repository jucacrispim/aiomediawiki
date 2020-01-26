# -*- coding: utf-8 -*-

import asyncio

from asynctest import CoroutineMock

from aiomediawiki import blocking


def test_blocking_fn():
    call = CoroutineMock(return_value=1)

    r = blocking.blocking(call)()

    assert r == 1


def test_blocking_mediawiki():
    mediawiki = blocking.BlockingMediaWiki()
    assert not asyncio.iscoroutinefunction(mediawiki.search)
