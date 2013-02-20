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


import os
import json
from tests.mocks import HandlerMock
from td.main import Model


class ModelTest(object):
    def setUp(self):
        self.model = Model()
        path = os.path.join(os.getcwd(), 'tests')
        self.model.setPath(os.path.join(path, '.td'))
        self.model.gpath = os.path.join(path, '.tdrc')
        self.tmppath = os.path.join(path, '.td~')

    def tearDown(self):
        try:
            os.remove(self.model.path)
            os.remove(self.tmppath)
            os.remove(self.model.gpath)
        except OSError:
            pass


class TestBackup(ModelTest):
    def test_should_create_backup_when_file_exists(self):
        self.model.add("testname1")
        self.model.add("testname2")
        assert os.path.exists(self.tmppath)
        assert json.loads(open(self.tmppath).read()) == {
            'items': [["testname1", 3, "", False, []]],
            'refs': {},
            'options': {}
        }


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

    def test_remove_non_existing_item(self):
        handler = HandlerMock()
        self.model.add("testname")
        self.model.remove("1.1")
        handler.assertLogged('No item found at index: 1.1')


class TestEdit(ModelTest):
    def setUp(self):
        super().setUp()
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

    def test_reparent_deeply_nested_item_to_same_parent(self):
        # corner case
        self.model.add("testname2", parent="1")
        self.model.add("testname3", parent="1.1")
        self.model.edit("1.1.1", parent="1.1")
        assert self.model == [
            ["testname", 3, "", False, [
                ["testname2", 3, "", False, [
                    ["testname3", 3, "", False, []]
                ]]
            ]]
        ]

    def test_edit_stability(self):
        # edit shouldn't move items around if not necessary
        self.model.add("testname2")
        self.model.edit("1", name="testname1", parent=-1)
        assert self.model == [
            ["testname1", 3, "", False, []],
            ["testname2", 3, "", False, []]
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
        super().setUp()
        self.model.add("testname")

    def test_get_top_level_item(self):
        assert self.model.get("1") == ["", "testname", 3, "", False, []]

    def test_get_second_level_item(self):
        self.model.add("testname2", parent="1")
        assert self.model.get("1.1") == ["1", "testname2", 3, "", False, []]


class ModifyTest(ModelTest):
    def setUp(self):
        super().setUp()
        self.model.add("testname1", priority=4)
        self.model.add("testname2")
        self.model.edit("1", done=True)

    def addSecondLevel(self):
        self.model.add("testname3", priority=2, parent="2")
        self.model.add("testname4", parent="2")

    def addThirdLevel(self):
        self.model.add("testname5", parent="2.1")
        self.model.add("testname6", priority=2, parent="2.1")

    def addComments(self):
        self.model.edit("1", comment="testcomment1")
        self.model.edit("2", comment="testcomment2")


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
            ["testname1", 4, "", True, []],
            ["testname2", 3, "", False, []]
        ]

    def test_sort_only_first_level_by_name(self):
        self.addSecondLevel()
        sort = (None, {1: (0, True)})
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
        sort = (None, {1: (1, False)})
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
        sort = (None, {2: (0, True)})
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
        sort = (None, {2: (1, True)})
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
        sort = (None, {1: (0, True), 3: (1, False)})
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
        sort = ((0, True), {2: (1, True)})
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

    def test_done_all_levels_comment_by_regexp(self):
        self.addSecondLevel()
        self.addComments()
        done = ((2, r'test.*[2|3]', True), {})
        result = self.model.modify(done=done)
        assert result == [
            ["testname1", 4, "testcomment1", True, []],
            ["testname2", 3, "testcomment2", True, [
                ["testname3", 2, "", False, []],
                ["testname4", 3, "", False, []]
            ]]
        ]

    def test_done_first_level(self):
        self.addSecondLevel()
        done = ((None, None, None), {1: (None, None, True)})
        result = self.model.modify(done=done)
        assert result == [
            ["testname1", 4, "", True, []],
            ["testname2", 3, "", True, [
                ["testname3", 2, "", False, []],
                ["testname4", 3, "", False, []]
            ]]
        ]

    def test_done_first_level_by_regexp(self):
        self.addSecondLevel()
        self.addComments()
        done = ((None, None, None), {1: (None, r'test.*[2|3]', True)})
        result = self.model.modify(done=done)
        assert result == [
            ["testname1", 4, "testcomment1", True, []],
            ["testname2", 3, "testcomment2", True, [
                ["testname3", 2, "", False, []],
                ["testname4", 3, "", False, []]
            ]]
        ]

    def test_done_first_level_comment_by_regexp(self):
        self.addSecondLevel()
        self.addComments()
        done = ((None, None, None), {1: (2, r'test.*[2|3]', True)})
        result = self.model.modify(done=done)
        assert result == [
            ["testname1", 4, "testcomment1", True, []],
            ["testname2", 3, "testcomment2", True, [
                ["testname3", 2, "", False, []],
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


class TestOptions(ModifyTest):
    def setUp(self):
        super().setUp()
        self.addSecondLevel()
        self.addThirdLevel()

    def getNewModel(self):
        model = Model()
        model.setPath(os.path.join(os.getcwd(), 'tests', '.td'))
        return model

    def test_sort(self):
        self.model.setOptions(sort=((1, False), {}))
        assert list(self.getNewModel()) == [
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, [
                    ["testname6", 2, "", False, []],
                    ["testname5", 3, "", False, []]
                ]],
                ["testname4", 3, "", False, []]
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_purge(self):
        self.model.setOptions(purge=True)
        assert list(self.getNewModel()) == [
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, [
                    ["testname5", 3, "", False, []],
                    ["testname6", 2, "", False, []]
                ]],
                ["testname4", 3, "", False, []]
            ]]
        ]

    def test_done(self):
        self.model.setOptions(done=((None, None, True), {}))
        assert list(self.getNewModel()) == [
            ["testname1", 4, "", True, []],
            ["testname2", 3, "", True, [
                ["testname3", 2, "", True, [
                    ["testname5", 3, "", True, []],
                    ["testname6", 2, "", True, []]
                ]],
                ["testname4", 3, "", True, []]
            ]]
        ]

    def test_global_only(self):
        self.model.setOptions(glob=True, sort=((1, False), {}))
        assert list(self.getNewModel()) == [
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, [
                    ["testname6", 2, "", False, []],
                    ["testname5", 3, "", False, []]
                ]],
                ["testname4", 3, "", False, []]
            ]],
            ["testname1", 4, "", True, []]
        ]

    def test_local_before_global(self):
        self.model.add("testname10")
        self.model.edit("1", name="testname11")
        self.model.setOptions(sort=((0, False), {}))
        self.model.setOptions(glob=True, sort=((0, True), {}))
        assert list(self.getNewModel()) == [
            ["testname10", 3, "", False, []],
            ["testname11", 4, "", True, []],
            ["testname2", 3, "", False, [
                ["testname3", 2, "", False, [
                    ["testname5", 3, "", False, []],
                    ["testname6", 2, "", False, []]
                ]],
                ["testname4", 3, "", False, []]
            ]]
        ]
