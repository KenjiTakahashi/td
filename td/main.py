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


import sys
import readline
from argparse import ArgumentParser
from td.model import Model
from td.logger import logs


__version__ = '0.2.1'


class InvalidPatternError(Exception):
    def __init__(self, k, msg):
        self.message = "{0}: {1}".format(msg, k)

    def __str__(self):
        return self.message


class View(object):
    """Class used to display items on the screen."""

    COLORS = [
        None, '\033[34m', '\033[36m',
        '\033[37m', '\033[33m', '\033[31m'
    ]
    DIM = '\033[2m'
    BRIGHT = '\033[1m'
    RESET = '\033[0m'

    def __init__(self, model, **opts):
        """Creates new View instance.

        Displays the Model contents, basing on :opts:, and exits.

        :model: Model instance.
        :opts: Additional options defining the View looks.

        """
        def _show(submodel, offset):
            numoffset = len(str(len(list(submodel)))) - 1
            for i, v in enumerate(submodel, start=1):
                (name, priority, comment, done, subitems) = v
                padding = " " * offset
                if i < 10:
                    padding += " " * numoffset
                print("{0}{1}{2}{3}{4}{5}{6}".format(
                    View.RESET, padding, View.COLORS[priority],
                    done and View.DIM or View.BRIGHT,
                    i, done and '-' or '.', name
                ))
                padding += " " * (len(str(i)) + 1)
                if comment:
                    print("{0}{1}({2})".format(padding, View.RESET, comment))
                _show(subitems, offset + 2 + numoffset)
        _show(model, 0)


class ParserMixin(object):
    """Mixin class holding init methods for different parts of the paser."""
    def initView(self, subparsers):
        """Initializes v(iew) cli arguments.

        :subparsers: Argparse subparser to attach to.

        """
        view = subparsers.add_parser(
            'v', aliases=['view'], help="modify the view"
        )
        view.add_argument(
            '-s', '--sort', nargs='?', const=True, help="sort the view"
        )
        view.add_argument(
            '-p', '--purge', action='store_true', help="hide completed items"
        )
        view.add_argument(
            '-d', '--done', nargs='?', const=True,
            help="show all items as done"
        )
        view.add_argument(
            '-D', '--undone', nargs='?', const=True,
            help="show all items as not done"
        )
        view.set_defaults(func=self.view)

    def initModify(self, subparsers):
        """Initializes m(odify) cli arguments.

        :subparsers: Argparse subparser to attach to.

        """
        modify = subparsers.add_parser(
            'm', aliases=['modify'], help="modify the database"
        )
        modify.add_argument(
            '-s', '--sort', nargs='?', const=True, help="sort the database"
        )
        modify.add_argument(
            '-p', '--purge', action='store_true',
            help="remove completed items"
        )
        modify.add_argument(
            '-d', '--done', nargs='?', const=True,
            help="mark all items as done"
        )
        modify.add_argument(
            '-D', '--undone', nargs='?', const=True,
            help="mark all items as not done"
        )
        modify.set_defaults(func=self.modify)

    def initAdd(self, subparsers):
        """Initializes a(dd) cli arguments.

        Uses some hackery to make parent argument nice and optional
        at the same time.

        :subparsers: Argparse subparser to attach to.

        """
        add_parent = ArgumentParser(add_help=False)
        add_parent.add_argument(
            'parent', nargs='?',
            help="parent index (omit to add top-level item)"
        )
        add = subparsers.add_parser(
            'a', aliases=['add'], parents=[add_parent], help="add new item"
        )
        add.add_argument('-n', '--name')
        add.add_argument('-p', '--priority', type=int)
        add.add_argument('-c', '--comment')
        add.set_defaults(func=self.add)

    def initEdit(self, subparsers):
        """Initializes e(dit) cli arguments.

        :subparsers: Argparse subparser to attach to.

        """
        edit = subparsers.add_parser(
            'e', aliases=['edit'],
            help="edit existing item (also used for reparenting)"
        )
        edit.add_argument('index', help="index of the item to edit")
        edit.add_argument('--parent', help="new parent index")
        edit.add_argument('-n', '--name', help="new name")
        edit.add_argument('-p', '--priority', type=int, help="new priority")
        edit.add_argument('-c', '--comment', help="new comment")
        edit.set_defaults(func=self.edit)

    def initRm(self, subparsers):
        """Initializes r(m) cli arguments.

        :subparsers: Argparse subparser to attach to.

        """
        rm = subparsers.add_parser(
            'r', aliases=['rm'], help="remove existing item"
        )
        rm.add_argument('index', help="index of the item to remove")
        rm.set_defaults(func=self.rm)

    def initDone(self, subparsers):
        """Initializes d(one) cli arguments.

        :subparsers: Argparse subparser to attach to.

        """
        done = subparsers.add_parser(
            'd', aliases=['done'], help="mark item as done"
        )
        done.add_argument('index', help="index of the item to mark")
        done.set_defaults(func=self.done)

    def initUndone(self, subparsers):
        """Initialized D (undone) cli arguments.

        :subparsers: Argparse subparser to attach to.

        """
        undone = subparsers.add_parser(
            'D', aliases=['undone'], help='mark item as not done'
        )
        undone.add_argument('index', help="index of the item to unmark")
        undone.set_defaults(func=self.undone)

    def initOptions(self, subparsers):
        """Initialized o(ptions) cli arguments.

        :subparsers: Argparse subparser to attach to.

        """
        options = subparsers.add_parser(
            'o', aliases=['options'], help="change options"
        )
        options.add_argument(
            '-g', '--global', dest='glob', action="store_true",
            help="Store specified options globally"
        )
        options.add_argument(
            '-s', '--sort', nargs='?', const=True,
            help="set option to sort the database"
        )
        options.add_argument(
            '-p', '--purge', action='store_true',
            help="set option to remove completed items"
        )
        options.add_argument(
            '-d', '--done', nargs='?', const=True,
            help="set option to mark all items as done"
        )
        options.add_argument(
            '-D', '--undone', nargs='?', const=True,
            help="set option to mark all items as not done"
        )
        options.set_defaults(func=self.options)


class Arg(ParserMixin):
    """Handles everything related to command line arguments parsing,
    patterns decoding and calling appropriate view/model manipulation methods.

    """

    def __init__(self, model):
        """Creates new Arg instance.

        Defines all necessary command line arguments, sub-parsers, etc.

        :model: Model instance.

        """
        self.model = model
        self.arg = ArgumentParser(
            description="A non-offensive, per project ToDo manager."
        )
        self.arg.add_argument(
            '-v', '--version', action='version', version=__version__
        )
        subparsers = self.arg.add_subparsers(title="available commands")
        self.initView(subparsers)
        self.initModify(subparsers)
        self.initAdd(subparsers)
        self.initEdit(subparsers)
        self.initRm(subparsers)
        self.initDone(subparsers)
        self.initUndone(subparsers)
        self.initOptions(subparsers)
        args = self.arg.parse_args()
        args.func(args)

    @logs
    def _getPattern(self, ipattern, done=None):
        """Parses sort pattern.

        :ipattern: A pattern to parse.
        :done:  If :ipattern: refers to done|undone,
        use this to indicate proper state.
        :returns: A pattern suitable for Model.modify.

        """
        if ipattern is None:
            return None
        if ipattern is True:
            if done is not None:
                return ([(None, None, done)], {})
            return ([(0, False)], {})

        def _getReverse(pm):
            return pm == '+'

        def _getIndex(k):
            try:
                return int(k)
            except ValueError:
                raise InvalidPatternError(k, "Invalid level number")

        def _getDone(p):
            v = p.split('=')
            if len(v) == 2:
                try:
                    return (Model.indexes[v[0]], v[1], done)
                except KeyError:
                    raise InvalidPatternError(v[0], 'Invalid field name')
            return (None, v[0], done)
        ipattern1 = list()
        ipattern2 = dict()
        for s in ipattern.split(','):
            if done is not None:
                v = done
            else:
                v = _getReverse(s[-1])
            k = s.split(':')
            if len(k) == 1:
                if done is not None:
                    ipattern1.append(_getDone(k[0]))
                    continue
                ko = k[0][:-1]
                try:
                    if len(k[0]) == 1:
                        k = 0
                    else:
                        k = Model.indexes[ko]
                except KeyError:
                    k = _getIndex(k[0][:-1])
                else:
                    ipattern1.append((k, v))
                    continue
                v = (0, v)
            elif len(k) == 2:
                try:
                    if done is not None:
                        v = _getDone(k[1])
                    else:
                        v = (Model.indexes[k[1][:-1]], v)
                    k = _getIndex(k[0])
                except KeyError:
                    raise InvalidPatternError(k[1][:-1], 'Invalid field name')
            else:
                raise InvalidPatternError(s, 'Unrecognized token in')
            ipattern2.setdefault(k, []).append(v)
        return (ipattern1, ipattern2)

    def _getDone(self, args):
        """Parses the done|undone state.

        :args: Arguments passed to the command.
        :returns: Pattern for done|undone or None if neither were specified.

        """
        if args.done:
            return self._getPattern(args.done, True)
        if args.undone:
            return self._getPattern(args.undone, False)

    def view(self, args):
        """Handles the 'v' command.

        :args: Arguments supplied to the 'v' command.

        """
        View(self.model.modify(
            sort=self._getPattern(args.sort),
            purge=args.purge,
            done=self._getDone(args)
        ))

    def modify(self, args):
        """Handles the 'm' command.

        :args: Arguments supplied to the 'm' command.

        """
        self.model.modifyInPlace(
            sort=self._getPattern(args.sort),
            purge=args.purge,
            done=self._getDone(args)
        )

    def add(self, args):
        """Handles the 'a' command.

        :args: Arguments supplied to the 'a' command.

        """
        kwargs = self.getKwargs(args)
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
            kwargs = self.getKwargs(args, values)
            if kwargs:
                self.model.edit(args.index, **kwargs)

    def rm(self, args):
        """Handles the 'r' command.

        :args: Arguments supplied to the 'r' command.

        """
        if self.model.exists(args.index):
            self.model.remove(args.index)

    def done(self, args):
        """Handles the 'd' command.

        :args: Arguments supplied to the 'd' command.

        """
        if self.model.exists(args.index):
            self.model.edit(args.index, done=True)

    def undone(self, args):
        """Handles the 'D' command.

        :args: Arguments supplied to the 'D' command.

        """
        if self.model.exists(args.index):
            self.model.edit(args.index, done=False)

    def options(self, args):
        """Handles the 'o' command.

        :args: Arguments supplied to the 'o' command.

        """
        self.model.setOptions(
            glob=args.glob,
            sort=self._getPattern(args.sort),
            purge=args.purge,
            done=self._getDone(args)
        )

    def getKwargs(self, args, values={}):
        """Gets necessary data from stdin.

        @note: Also displays error message when no item name is set.

        :args: Arguments supplied in command line.
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
                value = int(value)
            except ValueError:
                if value == '':
                    return None
                print("Invalid priority value!")
                exit(0)
            else:
                if value not in [1, 2, 3, 4, 5]:
                    print("Invalid priority value!")
                    exit(0)
                return value
        return value


def run():
    model = Model()
    if len(sys.argv) > 1:
        Arg(model)
    else:
        View(model)
