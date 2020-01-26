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


class ResultsCache:
    """Class to cache results from mediawiki.
    """

    def __init__(self):
        self._cache = {}

    def add(self, key, value):
        """Adds content to the cache

        :param key: The key used to store the cache.
        :param value: The cache contents.
        """
        self._cache[key] = value

    def get(self, key):
        """Returns a result from the cache. If it does not exist
        returns None.
        """
        return self._cache.get(key)

    def remove(self, key):
        """Removes contents from the cache.

        :param key: The key to remove from the cache.
        """

        self._cache.pop(key, None)

    def clean(self):
        """Cleans the entire cache."""

        self._cache = {}
