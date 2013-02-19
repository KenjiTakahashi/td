# -*- coding: utf-8 -*-
# This is a part of td @ http://github.com/KenjiTakahashi/td
# Karol "Kenji Takahashi" Woźniak © 2012 - 2013
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from tests.mocks import HandlerMock
from td.main import Arg


class Test_getPattern(object):
    def setUp(self):
        self.arg = Arg.__new__(Arg)  # Don't do this at home
        self.handler = HandlerMock()

    def test_sort_all_levels(self):
        result = self.arg._getPattern(True)
        assert result == ((0, False), {})

    def test_sort_one_specific_level(self):
        result = self.arg._getPattern("1+")
        assert result == (None, {1: (0, True)})

    def test_sort_two_specific_levels(self):
        result = self.arg._getPattern("1+,2-")
        assert result == (None, {1: (0, True), 2: (0, False)})

    def test_sort_all_levels_and_specific_level(self):
        result = self.arg._getPattern("+,1+")
        assert result == ((0, True), {1: (0, True)})

    def test_sort_all_levels_by_priority(self):
        result = self.arg._getPattern("priority+")
        assert result == ((1, True), {})

    def test_sort_specific_level_by_priority(self):
        result = self.arg._getPattern("1:priority+")
        assert result == (None, {1: (1, True)})

    def test_done_all(self):
        result = self.arg._getPattern(True, done=True)
        assert result == ((None, None, True), {})

    def test_done_all_by_regexp(self):
        result = self.arg._getPattern("test.*[1-9]", done=True)
        assert result == ((None, r'test.*[1-9]', True), {})

    def test_done_all_by_comment_regexp(self):
        result = self.arg._getPattern("comment=test.*[1-9]", done=True)
        assert result == ((2, r'test.*[1-9]', True), {})

    def test_done_specific_level_by_regexp(self):
        result = self.arg._getPattern("1:test.*[1-9]", done=True)
        assert result == (None, {1: (None, r'test.*[1-9]', True)})

    def test_done_specific_level_by_comment_regexp(self):
        result = self.arg._getPattern("1:comment=test.*[1-9]", done=True)
        assert result == (None, {1: (2, r'test.*[1-9]', True)})

    def test_passing_invalid_level_without_index(self):
        self.arg._getPattern("a+")
        self.handler.assertLogged('Invalid level number: a')

    def test_passing_invalid_level_with_index(self):
        self.arg._getPattern("a:name+")
        self.handler.assertLogged('Invalid level number: a')

    def test_passing_invalid_index_name(self):
        self.arg._getPattern("1:nema+")
        self.handler.assertLogged('Invalid field name: nema')

    def test_passing_too_much_data(self):
        self.arg._getPattern("1:name:sth")
        self.handler.assertLogged('Unrecognized token in: 1:name:sth')

    def test_passing_invalid_index_name_with_done(self):
        self.arg._getPattern("nema=.*", done=True)
        self.handler.assertLogged('Invalid field name: nema')
