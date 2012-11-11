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


import sys
import readline
from argparse import ArgumentParser
import colorama
from td.model import Model


__version__ = '0.1'


class View(object):
    """Docstring for View """

    def __init__(self, model, **opts):
        """Creates new View instance.

        Displays the Model contents, basing on :opts:, and exits.

        :model: Model instance.
        :opts: Additional options defining the View looks.

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
                padding += " " * (len(str(i)) + 1)
                if comment:
                    print("{0}{1}({2})".format(
                        padding,
                        colorama.Style.RESET_ALL,
                        comment
                    ))
                _show(subitems, offset + 2 + numoffset)
        _show(model, 0)


class Arg(object):
    """Docstring for Arg """

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
            '-d', '--done', nargs='?', help="show all items as done"
        )
        view.add_argument(
            '-D', '--undone', nargs='?', help="show all items as not done"
        )
        view.set_defaults(func=self.view)

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
            '-d', '--done', nargs='?', help="mark all items as done"
        )
        modify.add_argument(
            '-D', '--undone', nargs='?', help="mark all items as not done"
        )
        modify.set_defaults(func=self.modify)

        add = subparsers.add_parser('a', aliases=['add'], help="add new item")
        add.add_argument(
            '--parent', help="parent index (omit to add top-level item)"
        )
        add.add_argument('-n', '--name')
        add.add_argument('-p', '--priority', type=int)
        add.add_argument('-c', '--comment')
        add.set_defaults(func=self.add)

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

        rm = subparsers.add_parser(
            'r', aliases=['rm'], help="remove existing item"
        )
        rm.add_argument('index', help="index of the item to remove")
        rm.set_defaults(func=self.rm)

        done = subparsers.add_parser(
            'd', aliases=['done'], help="mark item as done"
        )
        done.add_argument('index', help="index of the item to mark")
        done.set_defaults(func=self.done)

        undone = subparsers.add_parser(
            'D', aliases=['undone'], help='mark item as not done'
        )
        undone.add_argument('index', help="index of the item to unmark")
        undone.set_defaults(func=self.undone)

        args = self.arg.parse_args()
        args.func(args)

    def _getSortPattern(self, sort):
        """@todo: Docstring for _getSortPattern

        :sort: @todo
        :returns: @todo

        """
        def _getReverse(pm):
            if pm == '+':
                return True
            elif pm == '-':
                return False
            return None  # raise something? error
        sort1 = None
        if sort[0] == '+':
            sort1 = True
        elif sort[0] == '-':
            sort1 = False
        if sort1 is not None:
            sort = sort[1:]
        try:
            sort2 = {int(v[:-1]): _getReverse(v[-1]) for v in sort.split(',')}
        except ValueError:
            pass  # raise something? log error
        return (sort1, sort2)

    def view(self, args):
        """Handles the 'v' command.

        :args: Arguments supplied to the 'v' command.

        """
        View(self.model.modify(
            sort=self._getSortPattern(args.sort), purge=args.purge
        ))

    def modify(self, args):
        """Handles the 'm' command.

        :args: Arguments supplied to the 'm' command.

        """
        self.model.modifyInPlace(purge=args.purge)

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
            self.model.rm(args.index)

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

    def getKwargs(self, args, values={}):
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
