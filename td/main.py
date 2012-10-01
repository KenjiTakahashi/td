#!/usr/bin/env python2
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
import json
from collections import UserList


class Model(UserList):
    """Docstring for Model """

    def load(self, filename=os.getcwd()):
        """Loads data from the specified permanent location.
        If no location is set, it defaults to current working dir.

        :filename: File location.

        """
        self._filename = filename
        try:
            data = json.loads(open(os.path.join(self._filename, '.td')).read())
        except IOError:
            self.refs = dict()
        else:
            self.extend(data['items'])
            self.refs = data['refs']

    def save(self):
        """Saves model data to permanent storage."""
        open(self._filename, 'w').write(
            json.dumps({'items': self.data, 'refs': self.refs})
        )

    def add(self, name, priority=3, comment="", parent=""):
        """Adds new item to the model.

        Name argument may contain (ref:) syntax, which will be
        stripped down as needed.

        :parent: should have a form "<itemref>.<subitemref...>" (e.g. "1.1").

        :name: Name (with refs).
        :priority: Item's priority.
        :comment: Comment.
        :parent: Item's parent ("" for top-level item).

        """
        item = (name, priority, comment, False, [])
        data = self.data
        for c in parent:
            try:
                i = int(c) - 1
            except ValueError:
                pass
            else:
                data = data[i][4]
        data.append(item)

    def remove(self, index):
        """Removes specified item from the model.

        :index: Should have a form "<itemref>.<subitemref...>" (e.g. "1.1").

        :index: Item's index.

        """
        data = self.data
        for j, c in enumerate(index):
            try:
                i = int(c) - 1
            except ValueError:
                pass
            else:
                if j + 1 == len(index):
                    try:
                        del data[i]
                    except IndexError:
                        pass  # logger
                else:
                    data = data[i][4]


class View(object):
    """Docstring for View """

    def __init__(self, model):
        """Creates new View instance.

        :model: Model instance.
        """
        self._model = model

    def show(self, opts):
        """Displays a list of model's items and exits.

        :opts: Additional options to customize view.

        """
        def _show(submodel, offset):
            for name, priority, comment, done, subitems in submodel:
                print(" " * offset, name)
                _show(subitems, offset + 4)
        _show(self._model, 0)


def run():
    """@todo: Docstring for run """
    model = Model()
    model.load()
    model.add("testname")
    model.add("testname2", parent="1")
    view = View(model)
    view.show(None)
