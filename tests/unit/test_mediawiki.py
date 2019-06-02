# -*- coding: utf-8 -*-
# Copyright 2019 Juca Crispim <juca@poraodojuca.net>

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

from asynctest import CoroutineMock
import pytest

from aiomediawiki import wiki


@pytest.fixture
def mediawiki():
    yield wiki.MediaWiki()


def test_api_url(mediawiki):
    exp = 'https://en.wikipedia.org/w/api.php'

    assert mediawiki.api_url == exp


@pytest.mark.asyncio
async def test_request2api(mocker, mediawiki):
    mocker.patch.object(wiki.yaar, 'get', CoroutineMock())
    params = {'some': 'thing'}
    await mediawiki.request2api(params)

    params = wiki.yaar.get.call_args[1]['params']
    assert params['format'] == 'json'


@pytest.mark.asyncio
async def test_search(mocker, mediawiki):
    ret = {'query': {'search': [{'title': 'one'}, {'title': 'two'}]}}
    mocker.patch.object(wiki.MediaWiki, 'request2api',
                        CoroutineMock(return_value=ret))

    r = await mediawiki.search('some query')

    assert len(r) == 2


@pytest.mark.asyncio
async def test_get_page_dont_load(mocker, mediawiki):
    mocker.patch.object(wiki.MediaWikiPage, 'load', CoroutineMock())
    mocker.patch.object(wiki.MediaWiki, 'LOAD_PAGE', False)

    p = await mediawiki.get_page('some title')

    assert not p.load.called


@pytest.mark.asyncio
async def test_get_page(mocker, mediawiki):
    mocker.patch.object(wiki.MediaWikiPage, 'load', CoroutineMock())
    mocker.patch.object(wiki.MediaWiki, 'LOAD_PAGE', True)

    p = await mediawiki.get_page('some title')

    assert p.load.called
