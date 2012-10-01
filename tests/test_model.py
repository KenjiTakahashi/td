# -*- coding: utf-8 -*-
# This is a part of td @ http://github.com/KenjiTakahashi/td
# Karol "Kenji Takahashi" Woźniak © 2012
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


from td.main import Model


class ModelTest(object):
    def setUp(self):
        self.model = Model()


class TestAdd(ModelTest):
    def test_add_top_level_item(self):
        self.model.add("testname")
        assert self.model == [("testname", 3, "", False, [])]

    def test_add_second_level_item(self):
        self.model.add("testname")
        self.model.add("testname2", parent="1")
        assert self.model == [("testname", 3, "", False, [
            ("testname2", 3, "", False, [])
        ])]


class TestRemove(ModelTest):
    def test_remove_item(self):
        self.model.add("testname")
        self.model.add("testname2", parent="1")
        self.model.remove("1")
        assert self.model == []

    def test_remove_child_item(self):
        self.model.add("testname")
        self.model.add("testname2", parent="1")
        self.model.remove("1.1")
        assert self.model == [("testname", 3, "", False, [])]
