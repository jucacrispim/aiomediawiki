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

__doc__ = """A wrapper to access the MediaWiki API.

Usage
-----
.. code-block:: python

    wiki = MediaWiki()
    # search for pages in wikipedia
    for title await wiki.search('some query'):
        print(title)

    # get a specific page
    page = await wiki.get_page(title)
    print(page.title)
    print(page.summary)


"""

import yaar

from .page import MediaWikiPage


MEDIAWIKI_API_URL = 'https://{lang}.wikipedia.org/w/api.php'


class MediaWiki:
    """A class used to search and get pages from mediawiki.
    """

    PAGE_CLS = MediaWikiPage
    """The page class"""

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
        response = await yaar.get(self.api_url, params=params)
        return response.json()

    async def search(self, query):
        """Performs a seach using the api.

        :param query: A string with the query
        """

        params = {'srsearch': query,
                  'list': 'search'}

        r = await self.request2api(params)
        results = r['query']['search']
        return [r['title'] for r in results]

    async def get_page(self, title):
        """Returns an instance of :class:`~aiomediawiki.wiki.MediaWikiPage`.
        """

        page = self.PAGE_CLS(self, title)
        if self.LOAD_PAGE:
            await page.load()

        return page
