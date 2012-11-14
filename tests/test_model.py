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
        self.model.add("testname1", priority=4)
        self.model.add("testname2")
        self.model.edit("1", done=True)


class TestModify(ModifyTest):
    def addSecondLevel(self):
        self.model.add("testname3", priority=2, parent="2")
        self.model.add("testname4", parent="2")

    def addThirdLevel(self):
        self.model.add("testname5", parent="2.1")
        self.model.add("testname6", priority=2, parent="2.1")

    def addComments(self):
        self.model.edit("1", comment="testcomment1")
        self.model.edit("2", comment="testcomment2")

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
            ["testname1", 4, "", True, []],
            ["testname2", 3, "", False, []]
        ]

    def test_sort_only_first_level_by_name(self):
        self.addSecondLevel()
        sort = (None, {0: (0, True)})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, []],
                ["testname4", 3, "", False, []]
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_sort_only_first_level_by_priority(self):
        self.addSecondLevel()
        sort = (None, {0: (1, False)})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, []],
                ["testname4", 3, "", False, []]
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_sort_only_second_level_by_name(self):
        self.addSecondLevel()
        sort = (None, {1: (0, True)})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname1", 4, "", True, []],
            ["testname2", 3, "", False, [
                ["testname4", 3, "", False, []],
                ["testname3", 2, "", False, []]
            ]]
        ]

    def test_sort_only_second_level_by_priority(self):
        self.addSecondLevel()
        sort = (None, {1: (1, True)})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname1", 4, "", True, []],
            ["testname2", 3, "", False, [
                ["testname4", 3, "", False, []],
                ["testname3", 2, "", False, []]
            ]]
        ]

    def test_sort_all_levels_by_name(self):
        self.addSecondLevel()
        self.addThirdLevel()
        sort = ((0, True), {})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname2", 3, "", False, [
                ["testname4", 3, "", False, []],
                ["testname3", 2, "", False, [
                    ["testname6", 2, "", False, []],
                    ["testname5", 3, "", False, []]
                ]]
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_sort_all_levels_by_priority(self):
        self.addSecondLevel()
        self.addThirdLevel()
        sort = ((1, False), {})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, [
                    ["testname6", 2, "", False, []],
                    ["testname5", 3, "", False, []]
                ]],
                ["testname4", 3, "", False, []]
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_sort_first_level_by_name_and_third_level_by_priority(self):
        self.addSecondLevel()
        self.addThirdLevel()
        sort = (None, {0: (0, True), 2: (1, False)})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, [
                    ["testname6", 2, "", False, []],
                    ["testname5", 3, "", False, []]
                ]],
                ["testname4", 3, "", False, []]
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_sort_second_level_by_priority_and_rest_by_name(self):
        self.addSecondLevel()
        self.addThirdLevel()
        sort = ((0, True), {1: (1, True)})
        result = self.model.modify(sort=sort)
        assert result == [
            ["testname2", 3, "", False, [
                ["testname4", 3, "", False, []],
                ["testname3", 2, "", False, [
                    ["testname6", 2, "", False, []],
                    ["testname5", 3, "", False, []]
                ]],
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_done_all_levels(self):
        self.addSecondLevel()
        done = ((None, None, True), {})
        result = self.model.modify(done=done)
        assert result == [
            ["testname1", 4, "", True, []],
            ["testname2", 3, "", True, [
                ["testname3", 2, "", True, []],
                ["testname4", 3, "", True, []]
            ]]
        ]

    def test_done_all_levels_by_regexp(self):
        self.addSecondLevel()
        self.addComments()
        done = ((None, r'test.*[1|2|3]', True), {})
        result = self.model.modify(done=done)
        assert result == [
            ["testname1", 4, "testcomment1", True, []],
            ["testname2", 3, "testcomment2", True, [
                ["testname3", 2, "", True, []],
                ["testname4", 3, "", False, []]
            ]]
        ]

    def test_done_all_levels_name_by_regexp(self):
        self.addSecondLevel()
        self.addComments()
        done = ((0, r'test.*[1|3]', True), {})
        result = self.model.modify(done=done)
        assert result == [
            ["testname1", 4, "testcomment1", True, []],
            ["testname2", 3, "testcomment2", False, [
                ["testname3", 2, "", True, []],
                ["testname4", 3, "", False, []]
            ]]
        ]


class TestModifyInPlace(ModifyTest):
    def test_if_changes_get_propagated_to_source_model(self):
        # We use purge here, but it doesn't matter.
        # Model.modifyInPlace calls Model.modify, so
        # see TestModify for different options tests.
        self.model.modifyInPlace(purge=True)
        assert self.model == [["testname2", 3, "", False, []]]
