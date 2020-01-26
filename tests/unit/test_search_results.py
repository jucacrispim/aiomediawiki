# -*- coding: utf-8 -*-

from asynctest import CoroutineMock, Mock
import pytest

from aiomediawiki import wiki


@pytest.mark.asyncio
async def test_fetch_all():
    r = [Mock(load=CoroutineMock())]
    results = wiki.SearchResults(r)

    await results.load_all()

    assert results[0].load.called


@pytest.mark.asyncio
async def test_aiter():
    r = [Mock(load=CoroutineMock())]
    results = wiki.SearchResults(r)

    async for _ in results:
        pass

    assert results[0].load.called
