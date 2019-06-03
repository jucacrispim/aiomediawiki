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

import pytest

from aiomediawiki import MediaWiki
from aiomediawiki.exceptions import AmbiguousPage


@pytest.fixture
def mediawiki():
    return MediaWiki(lang='pt')


@pytest.mark.asyncio
async def test_search(mediawiki):

    r = await mediawiki.search('São Paulo')

    assert 'São Paulo Futebol Clube' in r


@pytest.mark.asyncio
async def test_get_page(mediawiki):
    page = await mediawiki.get_page('São Paulo Futebol Clube')

    assert page.summary


@pytest.mark.asyncio
async def test_get_ambiguous_page(mediawiki):

    try:
        await mediawiki.get_page('Independente')
        err = None
    except AmbiguousPage as e:
        err = e

    assert err
    assert len(err.candidates) > 0
