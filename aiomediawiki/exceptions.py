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


class MissingPage(Exception):
    pass


class AmbiguousPage(Exception):

    def __init__(self, page_title, candidates):
        self.page_title = page_title
        self.candidates = candidates

        cands = '\n'.join(self.candidates)
        msg = 'Page {} is ambiguous. The possible candidates are:\n{}'.format(
            self.page_title, cands)
        super().__init__(msg)
