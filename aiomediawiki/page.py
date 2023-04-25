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

from decimal import Decimal
from logging import getLogger
import re

from .exceptions import MissingPage, AmbiguousPage, InvalidPage


logger = getLogger(__name__)


class MediaWikiPage:
    """A class representing a wiki page. Using this class
    you can load a page's contents.
    """

    DEFAULT_LOAD_TYPE = 'basic'
    """Indicates if we should load the full information by default."""

    def __init__(self, mediawiki, title=None, pageid=None):
        """Constructor for MediaWikiPage.

        :param mediawiki: An instance of :class:`~aiomediawiki.wiki.MediaWiki`.
        :param title: The page title.
        :param pageid: The id of the page.
        """

        if not any([title, pageid]):
            raise TypeError('You must pass either title or pageid')

        self.mediawiki = mediawiki
        self._title = title
        self._pageid = pageid
        self._summary = None
        self._redirected = False
        self._url = None
        self._links = None
        self._redirects = None
        self._references = None
        self._categories = None
        self._coordinates = None

    def __str__(self):  # pragma: no cover
        return 'MediaWikiPage: {}'.format(self.title)

    def __repr__(self):  # pragma: no cover
        return str(self)

    @classmethod
    def from_api_result(cls, mediawiki, result):
        """Creates an MediaWikiPage instance from a json result
        from the mediawiki api.

        :param mediawiki: An instance of :class:`~aiomediawiki.wiki.MediaWiki`.
        :param result: A result result from the mediawiki api.
        """
        inst = cls(mediawiki, result['title'], result['pageid'])
        inst._redirected = bool(result.get('redirects'))
        inst._pageid = result['pageid']
        inst._title = result['title']
        inst._url = result['fullurl']
        inst._summary = result['extract']
        inst._links = [link['title'] for link in result.get('links', [])]
        inst._redirects = [red['title'] for red in result.get('redirects', [])]
        inst._references = [ref['url'] for ref in result.get('extlinks', [])]
        inst._categories = [cat['title'].split(':', 1)[1]
                            for cat in result.get('categories', [])]
        inst._coordinates = inst._get_coordinates(result)

        return inst

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

    async def load(self, load_type=DEFAULT_LOAD_TYPE):
        """Fetches the page content from a mediawiki installation.

        :param load_type: Indicates if we should load everything,
          including image links and html or only the basic api info.
        """
        kw = {}
        if self.title:
            kw['titles'] = [self.title]

        if self.pageid:
            kw['pageids'] = [self.pageid]

        loader = self._get_loader()(self.mediawiki, **kw)
        gen = await loader.basic_load()
        page = None
        async for page in gen:  # pragma: no branch
            break

        assert page

        self._merge(page)

    def _merge(self, page):
        """Merges a page into this instance. If the pages have
        different pageid will raise InvalidPage
        """

        if self.pageid and self.pageid != page.pageid:
            raise InvalidPage(page)

        self._redirected = page.redirected
        self._pageid = page.pageid
        self._url = page.url
        self._title = page.title
        self._summary = page.summary
        self._links = page.links
        self._redirects = page.redirects
        self._references = page.references
        self._categories = page.categories
        self._coordinates = page.coordinates

    def _get_coordinates(self, page):
        coord = page.get('coordinates')
        if not coord:
            return ()

        lat, lon = coord[0]['lat'], coord[0]['lon']
        return (Decimal(lat), Decimal(lon))

    def _get_loader(self):
        return PageLoader


class PageLoader:
    """A PageLoader knows how to fetch content from mediawiki and
    create page instances based on it.
    """

    PAGE_CLS = MediaWikiPage

    def __init__(self, mediawiki, titles=None, pageids=None,
                 raise_on_error=True):
        """:param mediawiki: An :class:`~aiomediawiki.wiki.MediaWiki` instance.
        :param titles: A list of page titles.
        :param pageids: A list of page ids. This argument has precedence
          over titles.
        :param raise_on_error: If False don't raises MissingPage nor
          AmbiguousPage. Log the error instead.
        """

        if not any([titles, pageids]):
            raise TypeError('You must pass either titles or pageids.')

        self.mediawiki = mediawiki
        self.titles = titles
        self.pageids = pageids
        self.raise_on_error = raise_on_error

    async def basic_load(self):
        """First load to a page. Checks if it exists and
        if it is not a disambiguaiton page. No html parsing
        is done here unless the page is an ambiguous one. In this case
        we download and parse the disambiguation page html in order to
        raise an exception with more information.
        """
        p = 'extracts|redirects|links|coordinates|categories|extlinks'
        p += '|info|pageprops'
        params = {
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

        def fmt_list(lst):
            return '|'.join([str(i) for i in lst])

        if self.pageids:
            params['pageids'] = fmt_list(self.pageids)
        else:
            params['titles'] = fmt_list(self.titles)

        r = await self.mediawiki.request2api(params)
        return self._load_results(r)

    async def _load_results(self, r):
        for presult in r['query']['pages']:
            try:
                page = await self._load_page(presult)
            except (MissingPage, AmbiguousPage) as e:
                if self.raise_on_error:
                    raise
                logger.warning('Error loading page %s. %s',
                               presult['title'], type(e))
            else:
                yield page

    async def _load_page(self, presult):

        if presult.get('missing'):
            raise MissingPage(
                'The page {} does not exist'.format(presult['title']))

        if presult.get('pageprops'):
            # we raise shit inside the method. read the meth doc
            await self._raise_ambiguous_page(presult['title'])

        page = self.PAGE_CLS.from_api_result(self.mediawiki, presult)
        return page

    async def _raise_ambiguous_page(self, title):
        """When a page is ambiguous we fetch the revision content
        of the disambiguation page,  parse the content's text
        and show the possible terms in the exception.
        """

        params = {
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "*",
            "rvlimit": 1,
            'titles': title,
        }
        r = await self.mediawiki.request2api(params)
        page = r["query"]["pages"][0]
        content = page["revisions"][0]['slots']['main']['content']
        pat = re.compile(r'\[\[(.*)\]\]')
        candidates = [c.split('|')[0] for c in pat.findall(content)]
        raise AmbiguousPage(title, candidates)
