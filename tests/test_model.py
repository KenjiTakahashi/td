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


import os
from td.main import Model


class ModelTest(object):
    def setUp(self):
        self.model = Model()
        self.model.setPath(os.path.join(os.getcwd(), 'tests'))

    def tearDown(self):
        try:
            os.remove(os.path.join(self.model.path, '.td'))
        except OSError:
            pass


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


class TestEdit(ModelTest):
    def setUp(self):
        super(TestEdit, self).setUp()
        self.model.add("testname")

    def test_edit_name(self):
        self.model.edit("1", name="testname2")
        assert self.model == [["testname2", 3, "", False, []]]

    def test_edit_priority(self):
        self.model.edit("1", priority=4)
        assert self.model == [["testname", 4, "", False, []]]

    def test_edit_comment(self):
        self.model.edit("1", comment="testcomment")
        assert self.model == [["testname", 3, "testcomment", False, []]]

    def test_mark_as_done(self):
        self.model.edit("1", done=True)
        assert self.model == [["testname", 3, "", True, []]]

    def test_mark_as_undone(self):
        self.model.edit("1", done=True)
        self.model.edit("1", done=False)
        assert self.model == [["testname", 3, "", False, []]]

    def test_reparent(self):
        self.model.add("testname2", parent="1")
        self.model.add("testname3", parent="1.1")
        self.model.edit("1.1.1", parent="1")
        assert self.model == [["testname", 3, "", False, [
            ["testname2", 3, "", False, []], ["testname3", 3, "", False, []]
        ]]]

    def test_reparent_to_top_level(self):
        self.model.add("testname2", parent="1")
        self.model.add("testname3", parent="1.1")
        self.model.edit("1.1.1", parent=-1)
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


class TestGet(ModelTest):
    def setUp(self):
        super(TestGet, self).setUp()
        self.model.add("testname")

    def test_get_top_level_item(self):
        assert self.model.get("1") == ["", "testname", 3, "", False, []]

    def test_get_second_level_item(self):
        self.model.add("testname2", parent="1")
        assert self.model.get("1.1") == ["1", "testname2", 3, "", False, []]


class ModifyTest(ModelTest):
    def setUp(self):
        super(ModifyTest, self).setUp()
        self.model.add("testname1")
        self.model.add("testname2")
        self.model.edit("1", done=True)


class TestModify(ModifyTest):
    def test_purge_done_when_enabled(self):
        result = self.model.modify(purge=True)
        assert result == [["testname2", 3, "", False, []]]

    def test_purge_from_second_level(self):
        self.model.add("testname3", parent="1")
        result = self.model.modify(purge=True)
        assert result == [["testname2", 3, "", False, []]]

    def test_do_not_purge_when_disabled(self):
        result = self.model.modify()
        assert result == [
            ["testname1", 3, "", True, []],
            ["testname2", 3, "", False, []]
        ]


class TestModifyInPlace(ModifyTest):
    def test_purge_done_when_enabled(self):
        self.model.modifyInPlace(purge=True)
        assert self.model == [["testname2", 3, "", False, []]]

    def test_do_not_purge_when_disabled(self):
        self.model.modifyInPlace(purge=False)
        assert self.model == [
            ["testname1", 3, "", True, []],
            ["testname2", 3, "", False, []]
        ]
