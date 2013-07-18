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
import shutil
import json
import re
from collections import UserList
from td.logger import logs


class NoItemError(Exception):
    def __init__(self, k):
        self.message = "No item found at index [{}].".format(k)

    def __str__(self):
        return self.message


def devtodo(path):
    try:
        inp = open(os.path.join(path, '.todo')).read()
    except IOError:
        return None
    else:
        import xml.etree.ElementTree as etree
        tree = etree.fromstring(inp)

        def _build(subtree):
            _data = list()
            for elem in subtree:
                attr = elem.attrib
                comment = ""
                children = list()
                try:
                    child = elem[0]
                except IndexError:
                    pass
                else:
                    if child.tag == 'comment':
                        comment = child.text.strip()
                    else:
                        children = _build(elem)
                _data.append([
                    elem.text.strip(),
                    Model.priorities.index(attr['priority']),
                    comment, bool(attr.get('done')), children
                ])
            return _data
        data = _build(tree)
        open(os.path.join(path, '.td'), 'w').write(
            json.dumps({'items': data, 'refs': dict(), 'options': dict()})
        )
        return data


def load(func):
    """@decorator: Loads data before executing :func:."""
    def aux(self, *args, **kwargs):
        path = (hasattr(self, 'path') and self.path
                or os.path.join(os.getcwd(), '.td'))
        gpath = (hasattr(self, 'gpath') and self.gpath
                 or os.path.expanduser('~/.tdrc'))
        try:
            data = json.loads(open(path).read())
        except IOError:
            data = devtodo(os.path.dirname(path))
            if data is not None:
                self[:] = data
            self.refs = dict()
            self.options = dict()
        else:
            self[:] = data['items']
            self.refs = data['refs']
            self.options = data['options']
        try:
            self.globalOptions = json.loads(open(gpath).read())
        except IOError:
            self.globalOptions = dict()
        self.data = self._modifyInternal(
            sort=self.options.get('sort') or self.globalOptions.get('sort'),
            purge=self.options.get('purge') or self.globalOptions.get('purge'),
            done=self.options.get('done') or self.globalOptions.get('done')
        )
        return func(self, *args, **kwargs)
    return aux


def save(func):
    """@decorator: Saves data after executing :func:.

    Also performs modifications set as permanent options.

    """
    def aux(self, *args, **kwargs):
        out = func(self, *args, **kwargs)
        path = (hasattr(self, 'path') and self.path
                or os.path.join(os.getcwd(), '.td'))
        gpath = (hasattr(self, 'gpath') and self.gpath
                 or os.path.expanduser('~/.tdrc'))
        if os.path.exists(path):
            shutil.copy2(path, os.path.join(os.path.dirname(path), '.td~'))
        open(path, 'w').write(
            json.dumps({
                'items': self.data,
                'refs': self.refs,
                'options': self.options
            })
        )
        open(gpath, 'w').write(json.dumps(self.globalOptions))
        return out
    return aux


class Model(UserList):
    """A holder for all the td data.

    It keeps the actual data, the references and permanent options and
    provides an interface to manipulate them.

    """

    indexes = {
        "name": 0,
        "priority": 1,
        "comment": 2,
        "state": 3
    }
    priorities = [None, "lowest", "low", "medium", "high", "highest"]

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
        if parent == -1:
            parent = ''
        parent = self._split(parent)
        index = self._split(index)
        item = self.data
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
        if parent is not None and parent != index[:-1]:
            parentitem = self.data
            for c in parent:
                parentitem = parentitem[int(c) - 1][4]
            parentitem.append(item)
            parent = index[:-1]
            parentitem = self.data
            for c in parent:
                parentitem = parentitem[int(c) - 1][4]
            parentitem.remove(item)

    @save
    @load
    @logs
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
                    raise NoItemError('.'.join(index))
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
        except Exception:
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

    def _modifyInternal(self, *, sort=None, purge=False, done=None):
        """Creates a whole new database from existing one, based on given
        modifiers.

        :sort: pattern should look like this:
        ([(<index>, True|False)], {<level_index>: [(<index>, True|False)]}),
        where True|False indicate whether to reverse or not,
        <index> are one of Model.indexes and <level_index> indicate
        a number of level to sort.
        Of course, the lists above may contain multiple items.

        :done: patterns looks similar to :sort:, except that it has additional
        <regexp> values and that True|False means to mark as done|undone.

        @note: Should not be used directly. It was defined here, because
        :save: decorator needs undecorated version of Model.modify.

        :sort: Pattern on which to sort the database.
        :purge: Whether to purge done items.
        :done: Pattern on which to mark items as done/undone.
        :returns: New database, modified according to supplied arguments.

        """
        sortAll, sortLevels = sort is not None and sort or ([], {})
        doneAll, doneLevels = done is not None and done or ([], {})

        def _mark(v, i):
            if done is None:
                return v[:4]

            def _mark_(index, regexp, du):
                if du is None:
                    return v[:4]
                if index is None:
                    for v_ in v[:3]:
                        if regexp is None or re.match(regexp, str(v_)):
                            return v[:3] + [du]
                    return v[:4]
                if regexp is None or re.match(regexp, str(v[index])):
                    return v[:3] + [du]
            try:
                for doneLevel in doneLevels[i]:
                    result = _mark_(*doneLevel)
                if result is not None:
                    return result
            except KeyError:
                pass
            for doneAll_ in doneAll:
                result = _mark_(*doneAll_)
            if result is None:
                return v[:4]
            return result

        def _modify(submodel, i):
            _new = list()
            for v in submodel:
                if purge:
                    if not v[3]:
                        _new.append(_mark(v, i) + [_modify(v[4], i + 1)])
                else:
                    _new.append(_mark(v, i) + [_modify(v[4], i + 1)])
            levels = sortLevels.get(i) or sortLevels.get(str(i))
            for index, reverse in levels or sortAll:
                _new = sorted(_new, key=lambda e: e[index], reverse=reverse)
            return _new
        return _modify(self.data, 1)

    @load
    def modify(self, *, sort=None, purge=False, done=None):
        """Calls Model._modifyInternal after loading the database."""
        return self._modifyInternal(sort=sort, purge=purge, done=done)

    @save
    def modifyInPlace(self, *, sort=None, purge=False, done=None):
        """Like Model.modify, but changes existing database instead of
        returning a new one."""
        self.data = self.modify(sort=sort, purge=purge, done=done)

    @save
    @load
    def setOptions(self, glob=False, **kwargs):
        """Set option(s).

        :glob: If True, stores specified options globally.
        :kwargs: Dictionary of options and values to set.

        """
        if glob:
            self.globalOptions.update(kwargs)
        else:
            self.options.update(kwargs)

    @load
    def __iter__(self):
        return super().__iter__()

    def _split(self, index):
        """Splits :index: by '.', removing empty strings.

        If None is supplied, None is returned.

        :index: Index to split.
        :returns: :index: split by '.' or empty list, if there are no items.

        """
        if index is None:
            return None
        split = index.split('.')
        if split == ['']:
            return []
        return split
