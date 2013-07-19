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


from collections import deque
from tests.mocks import HandlerMock, StdoutMock, ArgMock, ModelMock, GetMock
from td.main import Arg, Parser, Get


class TestParser_part(object):
    def setUp(self):
        self.mock = StdoutMock()
        self.handler = HandlerMock()
        self.out1 = None
        self.out2 = None

    def tearDown(self):
        self.mock.undo()

    def func1(self, test=None):
        self.out1 = test

    def func2(self, test1=None, test2=None):
        self.out2 = (test1, test2)

    def test_help_message(self):
        parser = Parser("", ["td", "-h"])
        parser._part("test", "", {}, "help")
        self.mock.assertEqual("help\n")

    def test_one_argument(self):
        parser = Parser("", ["td", "-t", "value"])
        parser._part("test", self.func1, {"-t": ("test", True)}, "")
        assert self.out1 == "value"

    def test_argument_without_value(self):
        parser = Parser("", ["td", "-b"])
        parser._part("test", self.func1, {"-b": ("test", False)}, "")
        assert self.out1 is True

    def test_two_arguments(self):
        #It should break by induction further on.
        parser = Parser("", ["td", "-t1", "value1", "-t2", "value2"])
        parser._part("test", self.func2, {
            "-t1": ("test1", True), "-t2": ("test2", True)
        }, "")
        self.out2 == ("value1", "value2")

    def test_one_argument_for_two_arguments_func(self):
        parser = Parser("", ["td", "-t2", "value2"])
        parser._part("test", self.func2, {
            "-t1": ("test1", True), "-t2": ("test2", True)
        }, "")
        self.out2 == (None, "value2")

    def test_no_arguments(self):
        parser = Parser("", ["td"])
        parser._part("test", self.func1, {}, "", test=True)
        assert self.out1 is True

    def test_not_enough_arguments(self):
        parser = Parser("", ["td"])
        parser._part("test", "", {"-t": ("test", True)}, "")
        self.handler.assertLogged("test: Not enough arguments.")

    def test_missing_argument(self):
        parser = Parser("", ["td", "-t"])
        parser._part("test", "", {"-t": ("test", True)}, "")
        self.handler.assertLogged("test: Not enough arguments.")

    def test_wrong_argument(self):
        parser = Parser("", ["td", "-y"])
        parser._part("test", "", {"-t": ("test", True)}, "")
        self.handler.assertLogged("test: Unrecognized argument [-y].")


class TestParserrock(object):
    def setUp(self):
        self.mock = StdoutMock()
        self.handler = HandlerMock()
        self.parser = Parser(ArgMock(), ["td"])
        self.parser._part = self.mock_part
        self.out = False

    def tearDown(self):
        self.mock.undo()

    def mock_part(self, *args, **kwargs):
        self.out = True

    def do_part(self, *n):
        self.parser.argv = deque(n)
        self.parser.rock()

    def assert_part(self, *n):
        self.do_part(*n)
        assert self.out is True

    def test_v(self):
        self.assert_part("v")

    def test_view(self):
        self.assert_part("view")

    def test_m(self):
        self.assert_part("m")

    def test_modify(self):
        self.assert_part("modify")

    def test_a(self):
        self.assert_part("a")

    def test_add(self):
        self.assert_part("add")

    def test_e_without_index(self):
        self.do_part("e")
        self.handler.assertLogged("edit: Not enough arguments.")

    def test_e(self):
        self.assert_part("e", "1.1")

    def test_edit(self):
        self.assert_part("edit", "1.1")

    def test_r_without_index(self):
        self.do_part("r")
        self.handler.assertLogged("rm: Not enough arguments.")

    def test_r(self):
        self.assert_part("r", "1.1")

    def test_rm(self):
        self.assert_part("rm", "1.1")

    def test_d_without_index(self):
        self.do_part("d")
        self.handler.assertLogged("done: Not enough arguments.")

    def test_d(self):
        self.assert_part("d", "1.1")

    def test_done(self):
        self.assert_part("done", "1.1")

    def test_D_without_index(self):
        self.do_part("D")
        self.handler.assertLogged("undone: Not enough arguments.")

    def test_D(self):
        self.assert_part("D", "1.1")

    def test_undone(self):
        self.assert_part("undone", "1.1")

    def test_o(self):
        self.assert_part("o")

    def test_options(self):
        self.assert_part("options")

    def test_add_parent(self):
        #It deserves a separate test
        self.assert_part("a", "1.1")

    def test_wrong_command(self):
        self.do_part("dang")
        self.handler.assertLogged("td: Unrecognized command [dang].")


class TestGet(object):
    def setUp(self):
        self.mock = StdoutMock()
        self.get = Get()
        Get.input = self.func
        self.i = True
        self.v = ""

    def tearDown(self):
        self.mock.undo()

    def func(self, f):
        if self.i:
            self.i = False
            return self.v
        return "1"

    def test_correct_name(self):
        self.v = "test"
        result = self.get.get("name")
        assert result == "test"

    def test_empty_name(self):
        self.get.get("name")
        self.mock.assertEqual("Name cannot be empty.\n")

    def test_correct_comment(self):
        self.v = "test"
        result = self.get.get("comment")
        assert result == "test"

    def test_parent(self):
        #Anything is correct here. See docstring in the code.
        self.v = "1.1"
        result = self.get.get("parent")
        assert result == "1.1"

    def test_correct_priority_names(self):
        for n, ne in enumerate(["lowest", "low", "normal", "high", "highest"]):
            self.i = True
            self.v = ne
            result = self.get.get("priority")
            assert result == n + 1

    def test_incorrect_priority_name(self):
        self.v = "the highest"
        self.get.get("priority")
        self.mock.assertEqual(
            "Unrecognized priority number or name [the highest].\n"
        )

    def test_correct_priority_numbers(self):
        for n in range(1, 6):
            self.i = True
            self.v = str(n)
            result = self.get.get("priority")
            assert result == n

    def t_incorrect_priority_numbers(self, n):
        self.v = str(n)
        self.get.get("priority")
        self.mock.assertEqual(
            "Unrecognized priority number or name [{}].\n".format(n)
        )

    def test_incorrect_priority_number0(self):
        self.t_incorrect_priority_numbers(0)

    def test_incorrect_priority_number6(self):
        self.t_incorrect_priority_numbers(6)

    def test_empty_priority(self):
        result = self.get.get("priority")
        assert result is None


class TestArg_getPattern(object):
    def setUp(self):
        self.arg = Arg.__new__(Arg)  # Don't do this at home
        self.handler = HandlerMock()

    def test_sort_all_levels(self):
        result = self.arg._getPattern(True)
        assert result == ([(0, False)], {})

    def test_sort_one_specific_level(self):
        result = self.arg._getPattern("1+")
        assert result == ([], {1: [(0, True)]})

    def test_sort_two_specific_levels(self):
        result = self.arg._getPattern("1+,2-")
        assert result == ([], {1: [(0, True)], 2: [(0, False)]})

    def test_sort_all_levels_and_specific_level(self):
        result = self.arg._getPattern("+,1+")
        assert result == ([(0, True)], {1: [(0, True)]})

    def test_sort_all_levels_by_priority(self):
        result = self.arg._getPattern("priority+")
        assert result == ([(1, True)], {})

    def test_sort_all_levels_by_name_and_priority(self):
        result = self.arg._getPattern("-,priority+")
        assert result == ([(0, False), (1, True)], {})

    def test_sort_all_levels_by_state_and_priority(self):
        result = self.arg._getPattern("state-,priority+")
        assert result == ([(3, False), (1, True)], {})

    def test_sort_specific_level_by_priority(self):
        result = self.arg._getPattern("1:priority+")
        assert result == ([], {1: [(1, True)]})

    def test_sort_specific_level_by_name_and_priority(self):
        result = self.arg._getPattern("1-,1:priority+")
        assert result == ([], {1: [(0, False), (1, True)]})

    def test_sort_specific_level_by_state_and_priority(self):
        result = self.arg._getPattern("1:state-,1:priority+")
        assert result == ([], {1: [(3, False), (1, True)]})

    def test_done_all(self):
        result = self.arg._getPattern(True, done=True)
        assert result == ([(None, None, True)], {})

    def test_done_all_by_regexp(self):
        result = self.arg._getPattern("test.*[1-9]", done=True)
        assert result == ([(None, r'test.*[1-9]', True)], {})

    def test_done_all_by_comment_regexp(self):
        result = self.arg._getPattern("comment=test.*[1-9]", done=True)
        assert result == ([(2, r'test.*[1-9]', True)], {})

    def test_done_specific_level_by_regexp(self):
        result = self.arg._getPattern("1:test.*[1-9]", done=True)
        assert result == ([], {1: [(None, r'test.*[1-9]', True)]})

    def test_done_specific_level_by_comment_regexp(self):
        result = self.arg._getPattern("1:comment=test.*[1-9]", done=True)
        assert result == ([], {1: [(2, r'test.*[1-9]', True)]})

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

    def test_empty_should_stay_empty(self):
        result = self.arg._getPattern(None)
        assert result is None


class TestArg(object):
    def setUp(self):
        self.mock = StdoutMock()
        self.model = ModelMock()
        self.mock.resetArgv()

    def tearDown(self):
        self.mock.undo()

    def test_view(self):
        Arg(self.model)
        assert self.model.modify_val is True

    def test_modify(self):
        self.mock.addArgs("m", "-s", "sp", "-p", "-d", "dp", "-D", "Dp")
        Arg(self.model)
        assert self.model.modifyInPlace_val is True

    def test_add(self):
        self.mock.addArgs("a", "1.1", "-n", "n", "-p", "1", "-c", "c")
        Arg(self.model)
        assert self.model.add_val is True

    def test_edit(self):
        self.mock.addArgs(
            "e", "1.1", "--parent", "2.2",
            "-n", "n", "-p", "1", "-c", "c"
        )
        Arg(self.model)
        assert self.model.edit_val is True

    def test_rm(self):
        self.mock.addArgs("r", "1.1")
        Arg(self.model)
        assert self.model.rm_val is True

    def test_done(self):
        self.mock.addArgs("d", "1.1")
        Arg(self.model)
        assert self.model.done_val is True

    def test_undone(self):
        self.mock.addArgs("D", "1.1")
        Arg(self.model)
        assert self.model.undone_val is True

    def test_options(self):
        self.mock.addArgs("o", "-g", "-s", "sp", "-p", "-d", "dp", "-D", "Dp")
        Arg(self.model)
        assert self.model.options_val is True

    def test_getKwargs(self):
        arg = Arg.__new__(Arg)
        result = arg.getKwargs({"priority": 3}, {"comment": "test"}, GetMock())
        assert result == {
            "name": "mock",
            "comment": "test",
            "priority": 3,
            "parent": "mock"
        }
