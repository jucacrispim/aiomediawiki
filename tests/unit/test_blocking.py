# -*- coding: utf-8 -*-

import asyncio
from unittest.mock import AsyncMock, Mock
import pytest

from aiomediawiki import blocking


def test_blocking_fn():
    call = AsyncMock(return_value=1)

    r = blocking.blocking(call)()

    assert r == 1


def test_blocking_mediawiki():
    mediawiki = blocking.BlockingMediaWiki()
    assert not asyncio.iscoroutinefunction(mediawiki.search)
    assert asyncio.iscoroutinefunction(mediawiki.request2api)


@pytest.mark.asyncio
async def test_load_page():
    mediawiki = blocking.BlockingMediaWiki()
    mediawiki.request2api = AsyncMock(spec=mediawiki.request2api)
    page = blocking.BlockingMediaWikiPage(mediawiki, 'the title')
    page.load = Mock(__original__=AsyncMock())
    await mediawiki._load_page(page)
    assert page.load.__original__.called
