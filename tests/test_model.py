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
        assert self.model == [["testname", 3, "", False, []]]

    def test_add_second_level_item(self):
        self.model.add("testname")
        self.model.add("testname2", parent="1")
        assert self.model == [["testname", 3, "", False, [
            ["testname2", 3, "", False, []]
        ]]]


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
        assert self.model == [["testname", 3, "", False, []]]


class TestModify(ModelTest):
    def setUp(self):
        super(TestModify, self).setUp()
        self.model.add("testname")

    def test_modify_name(self):
        self.model.modify("1", name="testname2")
        assert self.model == [["testname2", 3, "", False, []]]

    def test_modify_priority(self):
        self.model.modify("1", priority=4)
        assert self.model == [["testname", 4, "", False, []]]

    def test_modify_comment(self):
        self.model.modify("1", comment="testcomment")
        assert self.model == [["testname", 3, "testcomment", False, []]]

    def test_reparent(self):
        self.model.add("testname2", parent="1")
        self.model.add("testname3", parent="1.1")
        self.model.modify("1.1.1", parent="1")
        assert self.model == [["testname", 3, "", False, [
            ["testname2", 3, "", False, []], ["testname3", 3, "", False, []]
        ]]]

    def test_reparent_to_top_level(self):
        self.model.add("testname2", parent="1")
        self.model.add("testname3", parent="1.1")
        self.model.modify("1.1.1", parent=-1)
        assert self.model == [
            ["testname", 3, "", False, [
                ["testname2", 3, "", False, []]
            ]],
            ["testname3", 3, "", False, []]
        ]


class TestExists(ModelTest):
    def test_existing_top_level_index(self):
        self.model.add("testname")
        assert self.model.exists("1")

    def test_existing_second_level_index(self):
        self.model.add("testname")
        self.model.add("testname2", parent="1")
        assert self.model.exists("1.1")

    def test_non_existing_top_level_index(self):
        assert not self.model.exists("1")

    def test_non_existing_second_level_index(self):
        self.model.add("testname")
        assert not self.model.exists("1.1")
