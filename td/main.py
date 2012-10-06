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
import sys
import readline
from collections import UserList
from argparse import ArgumentParser
import colorama


__version__ = '0.1'


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
    def modify(
        self, index, name=None, priority=None,
        comment=None, done=None, parent=None
    ):
        """Modifies :index: to specified data.

        Every argument, which is not None, will get changed.
        If parent is not None, the item will get reparented.
        Use parent=-1 or parent='' for reparenting to top-level.

        :index: Index of the item to modify.
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


class View(object):
    """Docstring for View """

    def __init__(self, model, opts=None):
        """Creates new View instance.

        Displays the Model contents, based on :opts: and exits.

        :model: Model instance.
        :opts: Additional options for View looks.

        """
        colors = [
            None, colorama.Fore.BLUE, colorama.Fore.CYAN,
            colorama.Fore.WHITE, colorama.Fore.YELLOW, colorama.Fore.RED
        ]
        colorama.init()

        def _show(submodel, offset):
            numoffset = len(str(len(list(submodel)))) - 1
            for i, v in enumerate(submodel, start=1):
                (name, priority, comment, done, subitems) = v
                padding = " " * offset
                if i < 10:
                    padding += " " * numoffset
                print("{0}{1}{2}{3}{4}{5}".format(
                    padding, colors[priority],
                    done and colorama.Style.DIM or colorama.Style.BRIGHT,
                    i, done and '-' or '.', name
                ))
                if comment:
                    print("{0}{1}({2})".format(
                        padding,
                        colorama.Style.RESET_ALL,
                        comment
                    ))
                _show(subitems, offset + 4)
        _show(model, 0)


class Arg(object):
    """Docstring for Arg """

    def __init__(self, model):
        """Creates new Arg instance.

        Defines all necessary command line arguments, sub-parsers, etc.

        :model: Model instance.

        """
        self.model = model
        self.arg = ArgumentParser(description="A non-offensive ToDo manager.")
        self.arg.add_argument(
            '-v', '--version', action='version', version=__version__
        )
        subparsers = self.arg.add_subparsers(title="available commands")
        add = subparsers.add_parser('a', aliases=['add'], help="add new item")
        add.add_argument('--parent',
            help="parent index (omit to add top-level item)"
        )
        add.add_argument('-n', '--name')
        add.add_argument('-p', '--priority', type=int)
        add.add_argument('-c', '--comment')
        add.set_defaults(func=self.add)
        edit = subparsers.add_parser('e', aliases=['edit'],
            help="edit existing item (also used for reparenting)"
        )
        edit.add_argument('index', help="index of the item to edit")
        edit.add_argument('--parent', help="new parent index")
        edit.add_argument('-n', '--name', help="new name")
        edit.add_argument('-p', '--priority', type=int, help="new priority")
        edit.add_argument('-c', '--comment', help="new comment")
        edit.set_defaults(func=self.edit)
        rm = subparsers.add_parser('r', aliases=['rm'],
            help="remove existing item"
        )
        rm.add_argument('index', help="index of the item to remove")
        rm.set_defaults(func=self.rm)
        done = subparsers.add_parser('d', aliases=['done'],
            help="mark item as done"
        )
        done.add_argument('index', help="index of the item to mark")
        done.set_defaults(func=self.done)
        undone = subparsers.add_parser('D', aliases=['undone'],
            help='mark item as not done'
        )
        undone.add_argument('index', help="index of the item to unmark")
        undone.set_defaults(func=self.undone)
        args = self.arg.parse_args()
        args.func(args)

    def add(self, args):
        """Handles the 'a' command.

        :args: Arguments supplied to the 'a' command.

        """
        kwargs = self.get_kwargs(args)
        if kwargs:
            self.model.add(**kwargs)

    def edit(self, args):
        """Handles the 'e' command.

        :args: Arguments supplied to the 'e' command.

        """
        if self.model.exists(args.index):
            values = dict(zip(
                ['parent', 'name', 'priority', 'comment', 'done'],
                self.model.get(args.index)
            ))
            kwargs = self.get_kwargs(args, values)
            if kwargs:
                self.model.modify(args.index, **kwargs)

    def rm(self, args):
        """Handles the 'r' command.

        :args: Arguments supplied to the 'r' command.

        """
        if self.model.exists(args.index):
            self.model.rm(args.index)

    def done(self, args):
        """Handles the 'd' command.

        :args: Arguments supplied to the 'd' command.

        """
        if self.model.exists(args.index):
            self.model.modify(args.index, done=True)

    def undone(self, args):
        """Handles the 'D' command.

        :args: Arguments supplied to the 'D' command.

        """
        if self.model.exists(args.index):
            self.model.modify(args.index, done=False)

    def get_kwargs(self, args, values={}):
        """Gets necessary data from stdin.

        @note: Also displays error message when no item name is set.

        :args: Arguments supplited with command line.
        :values: Default values dictionary, supplied for editing.
        :returns: A dictionary containing data gathered from stdin.

        """
        name = args.name or self.get('name', values.get('name'))
        if name:
            kwargs = dict()
            kwargs['name'] = name
            for field in ['priority', 'comment', 'parent']:
                value = values.get(field)
                fvalue = getattr(args, field) or self.get(field, value)
                if fvalue is not None:
                    kwargs[field] = fvalue
            return kwargs
        else:
            print("Item must have a name!")
            return None

    def get(self, field, value=None):
        """Gets :field: value from stdin.

        :field: Field's name.
        :value: Default value for editing.
        :returns: Value got from stdin.

        """
        readline.set_startup_hook(lambda: readline.insert_text(
            value is not None and str(value) or ""
        ))
        try:
            value = input("{0}> ".format(field))
        except KeyboardInterrupt:
            print()
            exit(0)
        readline.set_startup_hook()
        if field == 'priority':
            try:
                return int(value)
            except ValueError:
                return None
        return value


def run():
    model = Model()
    if len(sys.argv) > 1:
        Arg(model)
    else:
        View(model)
