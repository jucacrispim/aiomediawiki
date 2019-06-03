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

from decimal import Decimal
import re

from .exceptions import MissingPage, AmbiguousPage


class MediaWikiPage:
    """A class representing a wiki page. Using this class
    you can load a page's contens.
    """

    DEFAULT_LOAD_TYPE = 'basic'
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

    async def _raise_ambiguous_page(self):
        """When a page is ambiguous we fetch the revision content for
        of the disambiguation page,  parse the content's text
        and show the possible terms in the exception.
        """

        params = {
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "*",
            "rvlimit": 1,
            'titles': self.title,
        }
        r = await self.mediawiki.request2api(params)
        page = r["query"]["pages"][0]
        content = page["revisions"][0]['slots']['main']['content']
        pat = re.compile(r'\[\[(.*)\]\]')
        candidates = [c.split('|')[0] for c in pat.findall(content)]
        raise AmbiguousPage(self.title, candidates)

    async def _basic_load(self):
        """First load to a page. Checks if it exists and
        if it is not a disambiguaiton page. No html parsing
        is done here unless the page is an ambiguous one. In this case
        we download and parse the disambiguation page html in order to
        raise an exception with more information.
        """
        p = 'extracts|redirects|links|coordinates|categories|extlinks'
        p += '|info|pageprops'
        params = {
            'titles': self.title,
            'prop': p,
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
            'inprop': 'url',
            'ppprop': 'disambiguation',
            'redirects': '',
        }

        r = await self.mediawiki.request2api(params)
        page = r['query']['pages'][0]
        if page.get('missing'):
            raise MissingPage('The page {} does not exist'.format(self.title))

        if page.get('pageprops'):
            # we raise shit inside the method. read the meth doc
            await self._raise_ambiguous_page()

        self._redirected = bool(r['query'].get('redirects'))
        self._pageid = page['pageid']
        # change here in case of redirect
        self._title = page['title']
        self._url = page['fullurl']
        self._summary = page['extract']
        self._links = [l['title'] for l in page.get('links', [])]
        self._redirects = [red['title'] for red in page.get('redirects', [])]
        self._references = [ref['url'] for ref in page.get('extlinks', [])]
        self._categories = [cat['title'].split(':', 1)[1]
                            for cat in page.get('categories', [])]
        self._coordinates = self._get_coordinates(page)

    async def load(self, load_type=DEFAULT_LOAD_TYPE):
        """Fetches the page content from a mediawiki installation.

        :param loa_type: Indicates if we should load everything,
          including image links and html or only the basic api info.
        """
        ltypes = {
            'basic': (self._basic_load,),
        }

        pl = ltypes[load_type]
        for fn in pl:
            await fn()
