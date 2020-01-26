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

import os

from asynctest import CoroutineMock
import pytest

from aiomediawiki import wiki, page

from . import DATA_DIR


@pytest.fixture
def page_fix():
    mediawiki = wiki.MediaWiki()
    return page.MediaWikiPage(mediawiki, 'São Paulo Futebol Clube')


@pytest.mark.asyncio
async def test_basic_load_missing(page_fix):
    ret = {'query': {'pages': [{'missing': True}]}}
    page_fix.mediawiki.request2api = CoroutineMock(return_value=ret)

    with pytest.raises(page.MissingPage):
        await page_fix._basic_load()


@pytest.mark.asyncio
async def test_basic_load_ambiguous(page_fix):
    ret = {'query': {'pages': [{'pageprops': {'disambiguation': ""}}]}}
    page_fix.mediawiki.request2api = CoroutineMock(return_value=ret)
    page_fix._raise_ambiguous_page = CoroutineMock(
        side_effect=page.AmbiguousPage('title', []))

    with pytest.raises(page.AmbiguousPage):
        await page_fix._basic_load()


@pytest.mark.asyncio
async def test_basic_load_ok(page_fix):
    ret = {'query': {'pages': [
        {'pageid': 123,
         'title': 'My Page',
         'fullurl': 'http://bla.nada',
         'extract': 'some summary',
         'redirects': [{'title': 'some-redir'}],
         'categories': [{'title': 'Category:Some Category'}],
         'extlinks': [{'url': 'some.url'}]}]}}

    page_fix.mediawiki.request2api = CoroutineMock(return_value=ret)

    await page_fix._basic_load()

    called_params = page_fix.mediawiki.request2api.call_args[0][0]
    assert 'titles' in called_params

    assert page_fix.pageid
    assert page_fix.url
    assert page_fix.redirected is False
    assert page_fix.summary
    assert not page_fix.links
    assert page_fix.references
    assert page_fix.categories
    assert page_fix.redirects
    assert page_fix.coordinates == ()


@pytest.mark.asyncio
async def test_basic_load_ok_pageid(page_fix):
    page_fix._pageid = 123
    ret = {'query': {'pages': [
        {'pageid': 123,
         'title': 'My Page',
         'fullurl': 'http://bla.nada',
         'extract': 'some summary',
         'redirects': [{'title': 'some-redir'}],
         'categories': [{'title': 'Category:Some Category'}],
         'extlinks': [{'url': 'some.url'}]}]}}

    page_fix.mediawiki.request2api = CoroutineMock(return_value=ret)

    await page_fix._basic_load()

    called_params = page_fix.mediawiki.request2api.call_args[0][0]
    assert 'pageids' in called_params

    assert page_fix.pageid
    assert page_fix.url
    assert page_fix.redirected is False
    assert page_fix.summary
    assert not page_fix.links
    assert page_fix.references
    assert page_fix.categories
    assert page_fix.redirects
    assert page_fix.coordinates == ()


def test_get_coordinates_no_coords(page_fix):
    ret = {}

    r = page_fix._get_coordinates(ret)

    assert not r


def test_get_coordinates(page_fix):
    ret = {'coordinates': [{'lat': 12.232,
                            'lon': 23.234}]}

    r = page_fix._get_coordinates(ret)

    assert r


@pytest.mark.asyncio
async def test_load_basic(page_fix):
    page_fix._basic_load = CoroutineMock()
    page_fix._full_api_load = CoroutineMock()

    await page_fix.load(load_type='basic')

    assert page_fix._basic_load.called
    assert not page_fix._full_api_load.called


@pytest.mark.asyncio
async def test_raise_ambiguous_page(page_fix):
    fname = os.path.join(DATA_DIR, 'revcontent.txt')
    with open(fname) as fd:
        content = fd.read()

    page_dict = {'revisions': [{'slots': {'main': {'content': content}}}]}
    r = {'query': {'pages': [page_dict]}}

    page_fix.mediawiki.request2api = CoroutineMock(return_value=r)

    with pytest.raises(page.AmbiguousPage):
        await page_fix._raise_ambiguous_page()


def test_instance_no_title_no_id():
    with pytest.raises(TypeError):
        wiki.MediaWikiPage(wiki.MediaWiki())
