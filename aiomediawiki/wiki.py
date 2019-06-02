# -*- coding: utf-8 -*-
"""A wrapper to access the MediaWiki API.

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

from decimal import Decimal

import yaar

from .exceptions import MissingPage, AmbiguousPage

MEDIAWIKI_API_URL = 'https://{lang}.wikipedia.org/w/api.php'


class MediaWikiPage:
    """A class representing a wiki page. Using this class
    you can load a page's contens.
    """

    DEFAULT_LOAD_TYPE = 'full'
    """Indicates if we should load the full information by default."""

    def __init__(self, mediawiki, title):
        """Constructor for MediaWikiPage.

        :param mediawiki: An instance of :class:`~aiomediawiki.wiki.MediaWiki`.
        :param title: The page title.
        """

        self.mediawiki = mediawiki
        self._title = title
        self._pageid = None
        self._summary = None
        self._redirected = False
        self._url = None
        self._links = None
        self._redirects = None
        self._references = None
        self._categories = None
        self._coordinates = None

    @property
    def pageid(self):
        return self._pageid

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url

    @property
    def redirected(self):
        return self._redirected

    @property
    def summary(self):
        return self._summary

    @property
    def links(self):
        return self._links

    @property
    def redirects(self):
        return self._redirects

    @property
    def references(self):
        return self._references

    @property
    def categories(self):
        return self._categories

    @property
    def coordinates(self):
        return self._coordinates

    def _get_coordinates(self, page):
        coord = page.get('coordinates')
        if not coord:
            return ()

        lat, lon = coord[0]['lat'], coord[0]['lon']
        return (Decimal(lat), Decimal(lon))

    async def _basic_load(self):
        """First load to a page. Checks if it exists and
        if it is not a disambiguaiton page.
        """
        params = {
            'prop': 'info|pageprops',
            'inprop': 'url',
            'ppprop': 'disambiguation',
            'redirects': '',
            'titles': self.title
        }

        r = await self.mediawiki.request2api(params)
        page = r['query']['pages'][0]
        if page.get('missing'):
            raise MissingPage('The page {} does not exist'.format(self.title))

        if page.get('pageprops'):
            # an ambiguous one...
            raise AmbiguousPage

        self._redirected = bool(r['query'].get('redirects'))
        self._pageid = page['pageid']
        # change here in case of redirect
        self._title = page['title']
        self._url = page['fullurl']

    async def _full_api_load(self):
        """After the basic load is done you can use this method
        to load more attributes from the api. No html parsing is
        done here.
        """

        params = {
            'titles': self.title,
            'prop': 'extracts|redirects|links|coordinates|categories|extlinks',
            # summary
            'explaintext': '',
            'exintro': '',  # full first section for the summary!
            # redirects
            'rdprop': 'title',
            'rdlimit': 'max',
            # links
            'plnamespace': 0,
            'pllimit': 'max',
            # coordinates
            'colimit': 'max',
            # categories
            'cllimit': 'max',
            'clshow': '!hidden',
            # references
            'ellimit': 'max',
        }

        r = await self.mediawiki.request2api(params)
        page = r['query']['pages'][0]

        self._summary = page['extract']
        self._links = [l['title'] for l in page.get('links', [])]
        self._redirects = [red['title'] for red in page.get('redirects', [])]
        self._references = [ref['url'] for ref in page.get('extlinks', [])]
        self._categories = [cat['title'].split(':', 1)[1]
                            for cat in page.get('categories', [])]
        self._coordinates = self._get_coordinates(page)

    async def load(self, load_type=DEFAULT_LOAD_TYPE):
        ltypes = {
            'basic': (self._basic_load,),
            'full': (self._basic_load, self._full_api_load)
        }

        pl = ltypes[load_type]
        for fn in pl:
            await fn()


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
        self._lang = lang

    @property
    def api_url(self):
        return self._url.format(lang=self._lang)

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
