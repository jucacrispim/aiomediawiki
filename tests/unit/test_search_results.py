# -*- coding: utf-8 -*-

from asynctest import CoroutineMock, Mock, MagicMock
import pytest

from aiomediawiki import wiki


@pytest.mark.asyncio
async def test_load_all(mocker):
    mocker.patch.object(wiki.SearchResults, 'LOADER_CLS',
                        Mock(wiki.SearchResults.LOADER_CLS))
    wiki.SearchResults.LOADER_CLS.return_value.basic_load = CoroutineMock(
        spec=wiki.SearchResults.LOADER_CLS.basic_load,
        return_value=MagicMock())
    wiki.SearchResults.LOADER_CLS.return_value.basic_load.return_value.\
        __aiter__.return_value = [Mock()]

    r = [Mock(load=CoroutineMock())]
    mediawiki = Mock()
    mediawiki.request2api = CoroutineMock()
    results = wiki.SearchResults(mediawiki, r)
    await results.load_all()

    assert len(results) == 1


@pytest.mark.asyncio
async def test_aiter():
    r = [Mock(load=CoroutineMock())]
    mediawiki = Mock()
    results = wiki.SearchResults(mediawiki, r)

    async for _ in results:
        pass

    assert results[0].load.called
