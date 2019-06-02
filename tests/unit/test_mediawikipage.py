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
def page():
    mediawiki = wiki.MediaWiki()
    return wiki.MediaWikiPage(mediawiki, 'São Paulo Futebol Clube')


@pytest.mark.asyncio
async def test_basic_load_missing(page):
    ret = {'query': {'pages': [{'missing': True}]}}
    page.mediawiki.request2api = CoroutineMock(return_value=ret)

    with pytest.raises(wiki.MissingPage):
        await page._basic_load()


@pytest.mark.asyncio
async def test_basic_load_ambiguous(page):
    ret = {'query': {'pages': [{'pageprops': {'disambiguation': ""}}]}}
    page.mediawiki.request2api = CoroutineMock(return_value=ret)

    with pytest.raises(wiki.AmbiguousPage):
        await page._basic_load()


@pytest.mark.asyncio
async def test_basic_load_ok(page):
    ret = {'query': {'pages': [{'pageid': 123,
                                'title': 'My Page',
                                'fullurl': 'http://bla.nada'}]}}
    page.mediawiki.request2api = CoroutineMock(return_value=ret)

    await page._basic_load()

    assert page.pageid
    assert page.url
    assert page.redirected is False


def test_get_coordinates_no_coords(page):
    ret = {}

    r = page._get_coordinates(ret)

    assert not r


def test_get_coordinates(page):
    ret = {'coordinates': [{'lat': 12.232,
                            'lon': 23.234}]}

    r = page._get_coordinates(ret)

    assert r


@pytest.mark.asyncio
async def test_full_api_load(page):
    page_ret = {
        'extract': 'some summary',
        'redirects': [{'title': 'some-redir'}],
        'categories': [{'title': 'Category:Some Category'}],
        'extlinks': [{'url': 'some.url'}]
    }
    ret = {'query': {'pages': [page_ret]}}

    page.mediawiki.request2api = CoroutineMock(return_value=ret)

    await page._full_api_load()

    assert page.summary
    assert not page.links
    assert page.references
    assert page.categories
    assert page.redirects
    assert page.coordinates == ()


@pytest.mark.asyncio
async def test_load_basic(page):
    page._basic_load = CoroutineMock()
    page._full_api_load = CoroutineMock()

    await page.load(load_type='basic')

    assert page._basic_load.called
    assert not page._full_api_load.called


@pytest.mark.asyncio
async def test_load_full(page):
    page._basic_load = CoroutineMock()
    page._full_api_load = CoroutineMock()

    await page.load(load_type='full')

    assert page._basic_load.called
    assert page._full_api_load.called
