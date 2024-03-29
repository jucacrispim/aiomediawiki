# -*- coding: utf-8 -*-

# Copyright 2019-2020 Juca Crispim <juca@poraodojuca.net>

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

__doc__ = """A wrapper to access the MediaWiki API.

Usage
-----
.. code-block:: python

    wiki = MediaWiki()
    # search for pages in wikipedia
    for page in await wiki.search('some query'):
        print(page.title)
        await page.load()

    # you can use async for to load the page while iterating
    async for page in await wiki.search('some query'):
        print(page.summary)


    # to load all pages in the result at once
    results = await wiki.search('some query')
    await results.load_all()

    # get a specific page
    page = await wiki.get_page(title)
    print(page.title)
    print(page.summary)


"""

import json

import yaar

from .cache import ResultsCache
from .page import MediaWikiPage, PageLoader


MEDIAWIKI_API_URL = 'https://{lang}.wikipedia.org/w/api.php'


class SearchResults(list):
    """A list for the search results. It knows how to load
    the reults contents.
    """

    LOADER_CLS = PageLoader

    def __init__(self, mediawiki, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mediawiki = mediawiki

    async def __aiter__(self):
        for p in self:
            await p.load()
            yield p

    async def load_all(self):
        pageids = [p.pageid for p in self]
        loader = self.LOADER_CLS(self.mediawiki, pageids=pageids)
        self.clear()
        async for page in await loader.basic_load():  # pragma no branch
            self.append(page)


class MediaWiki:
    """A class used to search and get pages from mediawiki.
    """

    PAGE_CLS = MediaWikiPage
    """The page class"""

    SEARCH_RESULTS_CLS = SearchResults
    """The class that handle search results.
    """

    LOAD_PAGE = True
    """Should we load the page when getting it?"""

    def __init__(self, url=MEDIAWIKI_API_URL, lang='en'):
        """Constructor for MediaWiki.

        :param url: The url for the mediawiki api. Defaults to the
          public wikipedia api.
        :param lang: The language for the results. Defaults to `en`.
        """
        self._url = url
        self.lang = lang
        self.cache = ResultsCache()

    @property
    def api_url(self):
        return self._url.format(lang=self.lang)

    async def request2api(self, params):
        """Performs a GET request to the mediawiki api. Returns a
        dictionary with the json response

        :param params: A dict with the querystring parameters.
        """

        params['format'] = 'json'
        params['formatversion'] = '2'
        params['action'] = 'query'

        cached = self.cache.get(str(params))
        if cached:
            r = json.loads(cached)
            return r

        response = await yaar.get(self.api_url, params=params)
        self.cache.add(str(params), response.text)
        return response.json()

    async def search(self, query, limit=10, offset=0):
        """Performs a seach using the api.

        :param query: A string with the query
        """

        params = {'srsearch': query,
                  'srlimit': limit,
                  'sroffset': offset,
                  'list': 'search'}

        r = await self.request2api(params)
        results = r['query']['search']
        return self.SEARCH_RESULTS_CLS(
            self,
            [self.PAGE_CLS(self, r['title'], r['pageid']) for r in results]
        )

    async def get_page(self, title=None, pageid=None):
        """Returns an instance of :class:`~aiomediawiki.wiki.MediaWikiPage`.

        :param title: The page title
        :param pageid: The pageid
        """

        page = self.PAGE_CLS(self, title, pageid)
        if self.LOAD_PAGE:
            await self._load_page(page)

        return page

    async def _load_page(self, page):
        return await page.load()
