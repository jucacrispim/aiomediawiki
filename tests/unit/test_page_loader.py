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

import os

from asynctest import CoroutineMock
import pytest

from aiomediawiki import page, wiki

from tests.unit import DATA_DIR


@pytest.fixture
def page_loader():
    mediawiki = wiki.MediaWiki()
    yield page.PageLoader(mediawiki, titles=['A page', 'other page'],
                          raise_on_error=True)


def test_page_loader_no_titles_no_pageids():
    with pytest.raises(TypeError):
        page.PageLoader(wiki.MediaWiki())


@pytest.mark.asyncio
async def test_load_results_missing_page(page_loader):
    result = {'query': {'pages': [{'missing': True, 'title': 'A page'}]}}

    with pytest.raises(page.MissingPage):
        async for _ in page_loader._load_results(result):
            pass


@pytest.mark.asyncio
async def test_load_results_ambiguous_page(page_loader):
    result = {'query': {'pages': [{'pageprops': {'disambiguation': ""},
                                   'title': 'bla'}]}}
    page_loader._raise_ambiguous_page = CoroutineMock(
        spec=page_loader._raise_ambiguous_page,
        side_effect=page.AmbiguousPage('title', ['cand 1', 'cand 1']))

    with pytest.raises(page.AmbiguousPage):
        async for _ in page_loader._load_results(result):
            pass


@pytest.mark.asyncio
async def test_load_results(page_loader):

    result = {'query': {'pages': [
        {'pageid': 123,
         'title': 'My Page',
         'fullurl': 'http://bla.nada',
         'extract': 'some summary',
         'redirects': [{'title': 'some-redir'}],
         'categories': [{'title': 'Category:Some Category'}],
         'extlinks': [{'url': 'some.url'}]},

        {'missing': True, 'title': 'bla'}
    ]}}

    page_loader.raise_on_error = False
    lst = [pg async for pg in page_loader._load_results(result)]
    assert len(lst) == 1


@pytest.mark.asyncio
async def test_raise_ambiguous_page(page_loader):
    fname = os.path.join(DATA_DIR, 'revcontent.txt')
    with open(fname) as fd:
        content = fd.read()

    page_dict = {'revisions': [{'slots': {'main': {'content': content}}}]}
    r = {'query': {'pages': [page_dict]}}

    page_loader.mediawiki.request2api = CoroutineMock(return_value=r)

    with pytest.raises(page.AmbiguousPage):
        await page_loader._raise_ambiguous_page('page title')


@pytest.mark.asyncio
async def test_basic_load_titles(page_loader):
    page_loader.mediawiki.request2api = CoroutineMock(
        spec=page_loader.mediawiki.request2api)

    page_loader._load_results = CoroutineMock(spec=page_loader._load_results)

    await page_loader.basic_load()

    params = page_loader.mediawiki.request2api.call_args[0][0]

    assert params['titles'] == 'A page|other page'


@pytest.mark.asyncio
async def test_basic_load_pageids(page_loader):
    page_loader.mediawiki.request2api = CoroutineMock(
        spec=page_loader.mediawiki.request2api)

    page_loader._load_results = CoroutineMock(spec=page_loader._load_results)

    page_loader.pageids = [123, 456]
    await page_loader.basic_load()

    params = page_loader.mediawiki.request2api.call_args[0][0]

    assert params['pageids'] == '123|456'
