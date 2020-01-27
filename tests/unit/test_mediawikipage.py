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


from asynctest import CoroutineMock, Mock, MagicMock
import pytest

from aiomediawiki import wiki, page


@pytest.fixture
def page_fix():
    mediawiki = wiki.MediaWiki()
    return page.MediaWikiPage(mediawiki, 'São Paulo Futebol Clube')


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
async def test_load_title(page_fix, mocker):
    mocker.patch.object(page, 'PageLoader', Mock(spec=page.PageLoader))
    page.PageLoader.return_value.basic_load = CoroutineMock(
        spec=page.PageLoader.basic_load,
        return_value=MagicMock())
    page.PageLoader.return_value.basic_load.return_value.\
        __aiter__.return_value = [Mock()]
    page_fix._merge = Mock(spec=page_fix._merge)

    await page_fix.load()

    called_kw = page.PageLoader.call_args[1]
    assert called_kw['titles']
    assert page_fix._merge.called


@pytest.mark.asyncio
async def test_load_pageid(page_fix, mocker):
    mocker.patch.object(page, 'PageLoader', Mock(spec=page.PageLoader))
    page.PageLoader.return_value.basic_load = CoroutineMock(
        spec=page.PageLoader.basic_load,
        return_value=MagicMock())
    page.PageLoader.return_value.basic_load.return_value.\
        __aiter__.return_value = [Mock()]
    page_fix._merge = Mock(spec=page_fix._merge)

    page_fix._pageid = 123
    page_fix._title = None

    await page_fix.load()

    called_kw = page.PageLoader.call_args[1]
    assert called_kw['pageids']
    assert page_fix._merge.called


def test_merge_invalid_page(page_fix):
    other_page = page.MediaWikiPage(page_fix.mediawiki, pageid=123)
    page_fix._pageid = 456

    with pytest.raises(page.InvalidPage):
        page_fix._merge(other_page)


def test_merge_ok(page_fix):
    other_page = page.MediaWikiPage(page_fix.mediawiki, pageid=123)
    other_page._summary = 'bla'
    page_fix._pageid = 123

    page_fix._merge(other_page)

    assert page_fix.summary == 'bla'


def test_instance_no_title_no_id():
    with pytest.raises(TypeError):
        wiki.MediaWikiPage(wiki.MediaWiki())
