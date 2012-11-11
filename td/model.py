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


def load(func):
    """@decorator: Loads data before executing :func:."""
    def aux(self, *args, **kwargs):
        path = hasattr(self, 'path') and self.path or os.getcwd()
        try:
            data = json.loads(open(os.path.join(path, '.td')).read())
        except IOError:
            self.refs = dict()
        else:
            self[:] = data['items']
            self.refs = data['refs']
        return func(self, *args, **kwargs)
    return aux


def save(func):
    """@decorator: Saves data after executing :func:."""
    def aux(self, *args, **kwargs):
        out = func(self, *args, **kwargs)
        path = hasattr(self, 'path') and self.path or os.getcwd()
        open(os.path.join(path, '.td'), 'w').write(
            json.dumps({'items': self.data, 'refs': self.refs})
        )
        return out
    return aux


class Model(UserList):
    """Docstring for Model """

    def setPath(self, path):
        """Sets permanent storage path.

        :path: New permanent storage path.

        """
        self.path = path

    @save
    @load
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

    @save
    @load
    def edit(
        self, index, name=None, priority=None,
        comment=None, done=None, parent=None
    ):
        """Modifies :index: to specified data.

        Every argument, which is not None, will get changed.
        If parent is not None, the item will get reparented.
        Use parent=-1 or parent='' for reparenting to top-level.

        :index: Index of the item to edit.
        :name: New name.
        :priority: New priority.
        :comment: New comment.
        :done: Done mark.
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
        if done is not None:
            item[3] = done
        if parent is not None and parent != '':
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

    @save
    @load
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

    @load
    def exists(self, index):
        """Checks whether :index: exists in the Model.

        :index: Index to look for.
        :returns: True if :index: exists in the Model, False otherwise.

        """
        data = self.data
        try:
            for c in self._split(index):
                i = int(c) - 1
                data = data[i][4]
        except:
            return False
        return True

    @load
    def get(self, index):
        """Gets data values for specified :index:.

        :index: Index for which to get data.
        :returns: A list in form
        [parent, name, priority, comment, done, children].

        """
        data = self.data
        index2 = self._split(index)
        for c in index2[:-1]:
            i = int(c) - 1
            data = data[i][4]
        return [index[:-2] or ""] + data[int(index[-1]) - 1]

    @load
    def modify(self, sort=False, purge=False, done=False, undone=False):
        """@todo: Docstring for modify

        :purge: @todo
        :done: @todo
        :undone: @todo
        :returns: @todo

        """
        pass

    @load
    def __iter__(self):
        return super(Model, self).__iter__()

    def _split(self, index):
        """Splits :index: by '.', removing empty strings.

        :index: Index to split.
        :returns: :index: split by '.' or empty list, if there are no items.

        """
        split = index.split('.')
        if split == ['']:
            return []
        return split
