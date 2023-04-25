# -*- coding: utf-8 -*-

from unittest.mock import AsyncMock, Mock, MagicMock

import pytest

from aiomediawiki import wiki


@pytest.mark.asyncio
async def test_load_all(mocker):
    mocker.patch.object(wiki.SearchResults, 'LOADER_CLS',
                        Mock(wiki.SearchResults.LOADER_CLS))
    wiki.SearchResults.LOADER_CLS.return_value.basic_load = AsyncMock(
        return_value=MagicMock())
    wiki.SearchResults.LOADER_CLS.return_value.basic_load.return_value.\
        __aiter__.return_value = [Mock()]

    r = [Mock(load=AsyncMock())]
    mediawiki = Mock()
    mediawiki.request2api = AsyncMock()
    results = wiki.SearchResults(mediawiki, r)
    await results.load_all()

    assert len(results) == 1


@pytest.mark.asyncio
async def test_aiter():
    r = [Mock(load=AsyncMock())]
    mediawiki = Mock()
    results = wiki.SearchResults(mediawiki, r)

    async for _ in results:
        pass

    assert results[0].load.called
