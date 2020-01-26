# -*- coding: utf-8 -*-

import asyncio

from asynctest import CoroutineMock
import pytest

from aiomediawiki import blocking


def test_blocking_fn():
    call = CoroutineMock(return_value=1)

    r = blocking.blocking(call)()

    assert r == 1


def test_blocking_mediawiki():
    mediawiki = blocking.BlockingMediaWiki()
    assert not asyncio.iscoroutinefunction(mediawiki.search)
    assert asyncio.iscoroutinefunction(mediawiki.request2api)


@pytest.mark.asyncio
async def test_load_page(mocker):
    mediawiki = blocking.BlockingMediaWiki()
    page = blocking.BlockingMediaWikiPage(mediawiki, 'the title')
    page._basic_load = CoroutineMock(spec=page._basic_load)
    await mediawiki._load_page(page)
    assert page._basic_load.called


def test_load_all_results():
    mediawiki = blocking.BlockingMediaWiki()

    def create_page():
        page = blocking.BlockingMediaWikiPage(mediawiki, 'the page')
        page._basic_load = CoroutineMock(spec=page._basic_load)
        return page

    results = [create_page() for i in range(5)]

    s_res = blocking.BlockingSearchResults(results)
    s_res.load_all()

    for r in results:
        assert r._basic_load.called
