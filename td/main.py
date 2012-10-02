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
from argparse import ArgumentParser


__version__ = '0.1'


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
        item = [name, priority, comment, False, []]
        data = self.data
        for c in self._split(parent):
            data = data[int(c) - 1][4]
        data.append(item)

    def modify(
        self, index, name=None, priority=None, comment=None, parent=None
    ):
        """Modifies :index: to specified data.

        Every argument, which is not None, will get changed.
        If parent is not None, the item will get reparented.
        Use parent=-1 for reparenting to top-level.

        :index: Index of the item to modify.
        :name: New name.
        :priority: New priority.
        :comment: New comment.
        :parent: New parent.

        """
        item = self.data
        index = self._split(index)
        for j, c in enumerate(index):
            item = item[int(c) - 1]
            if j + 1 != len(index):
                item = item[4]
        if name is not None:
            item[0] = name
        if priority is not None:
            item[1] = priority
        if comment is not None:
            item[2] = comment
        if parent is not None:
            if parent == -1:
                self.append(item)
            else:
                parentitem = self.data
                for c in self._split(parent):
                    parentitem = parentitem[int(c) - 1]
                parentitem[4].append(item)
            parent = index[:-1]
            parentitem = self.data
            for c in parent:
                parentitem = parentitem[int(c) - 1][4]
            parentitem.remove(item)

    def remove(self, index):
        """Removes specified item from the model.

        :index: Should have a form "<itemref>.<subitemref...>" (e.g. "1.1").

        :index: Item's index.

        """
        data = self.data
        index = self._split(index)
        for j, c in enumerate(index):
            i = int(c) - 1
            if j + 1 == len(index):
                try:
                    del data[i]
                except IndexError:
                    pass  # logger
            else:
                data = data[i][4]

    def _split(self, index):
        """Splits :index: by '.', removing empty strings.

        :index: Index to split.
        :returns: :index: split by '.' or empty list, if there are no items.

        """
        split = index.split('.')
        if split == ['']:
            return []
        return split


class View(object):
    """Docstring for View """

    def __init__(self, model):
        """Creates new View instance.

        :model: Model instance.

        """
        self._model = model

    def show(self, opts):
        """Displays a list of model's items and exits.

        :opts: Additional options to customize the view.

        """
        def _show(submodel, offset):
            for name, priority, comment, done, subitems in submodel:
                print(" " * offset, name)
                _show(subitems, offset + 4)
        _show(self._model, 0)


class Arg(object):
    """Docstring for Arg """

    def __init__(self):
        """Creates new Arg instance.

        Defines all necessary command line arguments, sub-parsers, etc.

        """
        self.arg = ArgumentParser(description="A non-offensive ToDo manager.")
        self.arg.add_argument(
            '-v', '--version', action='version', version=__version__
        )
        subparsers = self.arg.add_subparsers()
        add = subparsers.add_parser('a', aliases=['add'], help="ah")
        rm = subparsers.add_parser('r', aliases=['rm'], help="rh")
        done = subparsers.add_parser('d', aliases=['done'], help="dh")
        edit = subparsers.add_parser('e', aliases=['edit'], help="eh")
        self.arg.parse_args()


def run():
    """@todo: Docstring for run """
    model = Model()
    model.load()
    model.add("testname")
    model.add("testname2", parent="1")
    model.add("testname3", parent="1.1")
    #view = View(model)
    #view.show(None)
    Arg()
