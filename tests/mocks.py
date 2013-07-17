# -*- coding: utf-8 -*-
# This is a part of td @ http://github.com/KenjiTakahashi/td
# Karol "Kenji Takahashi" Woźniak © 2013
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


import logging
import sys
from io import StringIO


class HandlerMock(logging.Handler):
    def __init__(self):
        super(HandlerMock, self).__init__()
        self.message = None
        logging.getLogger('td').addHandler(self)

    def emit(self, record):
        self.message = str(record.msg)

    def assertLogged(self, message):
        assert self.message == message


class StdoutMock(object):
    def __init__(self):
        sys.stdout = StringIO()
        self.argv = sys.argv

    def undo(self):
        sys.argv = self.argv
        sys.stdout = sys.__stdout__

    def resetArgv(self):
        sys.argv = ['td']

    def addArgs(self, *args):
        sys.argv.extend(args)

    def assertEqual(self, msg):
        assert msg == sys.stdout.getvalue()


class ModelMock(object):
    def __init__(self):
        self.modify_val = False
        self.modifyInPlace_val = False
        self.add_val = False
        self.edit_val = False
        self.rm_val = False
        self.done_val = False
        self.undone_val = False
        self.options_val = False

    def get(self, index):
        return [1, 1, 1, 1, 1]

    def exists(self, index):
        return True

    def modify(self, sort, purge, done):
        self.modify_val = True

    def modifyInPlace(self, sort, purge, done):
        self.modifyInPlace_val = True

    def add(self, name, priority, comment, parent):
        self.add_val = True

    def edit(
        self, index=None, name=None, priority=None,
        comment=None, done=None, parent=None
    ):
        self.edit_val = True
        if done is True:
            self.done_val = True
        elif done is False:
            self.undone_val = True

    def remove(self, index):
        self.rm_val = True

    def setOptions(self, glob, sort, purge, done):
        self.options_val = True


class ArgMock(object):
    def __init__(self):
        self.model = ModelMock()

    def view(self):
        pass

    def modify(self):
        pass

    def add(self):
        pass

    def edit(self):
        pass

    def rm(self):
        pass

    def done(self):
        pass

    def undone(self):
        pass

    def options(self):
        pass
