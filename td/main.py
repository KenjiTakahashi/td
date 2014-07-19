# -*- coding: utf-8 -*-
# This is a part of td @ http://github.com/KenjiTakahashi/td
# Karol "Kenji Takahashi" Woźniak © 2012 - 2014
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
import readline
import sys
from td.model import Model
from td.logger import logs


__version__ = '0.4'


class EException(Exception):
    def __str__(self):
        return self.message


class InvalidPatternError(EException):
    def __init__(self, k, msg):
        self.message = "{}: {}".format(msg, k)


class UnrecognizedArgumentError(EException):
    def __init__(self, name, arg):
        self.message = "{}: Unrecognized argument [{}].".format(name, arg)


class UnrecognizedCommandError(EException):
    def __init__(self, name, cmd):
        self.message = "{}: Unrecognized command [{}].".format(name, cmd)


class NotEnoughArgumentsError(EException):
    def __init__(self, name):
        self.message = "{}: Not enough arguments.".format(name)


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
        :opts: Options defining how the View looks.

        """
        colors = not opts.get("nocolor")

        def _show(submodel, offset):
            numoffset = len(str(len(list(submodel)))) - 1
            for i, v in enumerate(submodel, start=1):
                (name, priority, comment, done, subitems) = v
                padding = " " * offset
                if i < 10:
                    padding += " " * numoffset
                print("{}{}{}{}{}{}{}".format(
                    colors and View.RESET or "",
                    padding,
                    colors and View.COLORS[priority] or "",
                    colors and (done and View.DIM or View.BRIGHT) or "",
                    i, done and '-' or '.', name
                ))
                padding += " " * (len(str(i)) + 1)
                if comment:
                    print("{}{}({})".format(
                        padding,
                        colors and View.RESET or "",
                        comment
                    ))
                _show(subitems, offset + 2 + numoffset)
        _show(model, 0)


class Parser(object):
    """Parses command line arguments and runs appropriate Arg methods."""

    def __init__(self, arg, argv):
        """Creates new Parser instance.

        First element of :argv: should be irrelevant (e.g. apps' name),
        because it will be stripped off.

        :arg: Arg instance.
        :argv: A list from which to get arguments.

        """
        self.arg = arg
        self.argv = deque(argv[1:])

    @logs
    def _part(self, name, func, args, help, **kwargs):
        """Parses arguments of a single command (e.g. 'v').

        If :args: is empty, it assumes that command takes no further arguments.

        :name: Name of the command.
        :func: Arg method to execute.
        :args: Dictionary of CLI arguments pointed at Arg method arguments.
        :help: Commands' help text.
        :kwargs: Additional arguments for :func:.

        """
        while self.argv:
            arg = self.argv.popleft()
            if arg == "-h" or arg == "--help":
                print(help)
                return
            try:
                argname, argarg = args[arg]
                kwargs[argname] = argarg and self.argv.popleft() or True
            except KeyError:
                raise UnrecognizedArgumentError(name, arg)
            except IndexError:
                valids = ["-s", "--sort", "-d", "--done", "-D", "--undone"]
                if arg not in valids:
                    raise NotEnoughArgumentsError(name)
                kwargs[argname] = True
        func(**kwargs)

    @logs
    def rock(self):
        """Starts and does the parsing."""
        if not self.argv:
            self.arg.view()
        while(self.argv):
            arg = self.argv.popleft()
            if arg == "-h" or arg == "--help":
                print(
                    """Usage: td [-h (--help)] [-v (--version)] [command]"""
                    """, where [command] is one of:\n\n"""
                    """v (view)\tChanges the way next output"""
                    """ will look like. See [td v -h].\n"""
                    """m (modify)\tApplies one time changes to"""
                    """ the database. See [td m -h].\n"""
                    """o (options)\tSets persistent options, applied"""
                    """ on every next execution. See [td o -h].\n"""
                    """a (add)\t\tAdds new item. See [td a -h].\n"""
                    """e (edit)\tEdits existing item. See [td e -h].\n"""
                    """r (rm)\t\tRemoves existing item. See [td r -h].\n"""
                    """d (done)\tMarks items as done. See [td d -h].\n"""
                    """D (undone)\tMarks items as not done. See [td D -h].\n"""
                    """\nAdditional options:\n"""
                    """  -h (--help)\tShows this screen.\n"""
                    """  -v (--version)Shows version number."""
                )
            elif arg == "-v" or arg == "--version":
                print("td :: {}".format(__version__))
            elif arg == "v" or arg == "view":
                self._part("view", self.arg.view, {
                    "--no-color": ("nocolor", False),
                    "-s": ("sort", True), "--sort": ("sort", True),
                    "-p": ("purge", False), "--purge": ("purge", False),
                    "-d": ("done", True), "--done": ("done", True),
                    "-D": ("undone", True), "--undone": ("undone", True)
                },
                    """Usage: td v [-h (--help)] [command(s)]"""
                    """, where [command(s)] are any of:\n\n"""
                    """-s (--sort) <pattern>\tSorts the output using"""
                    """ <pattern>.\n"""
                    """-p (--purge)\t\tHides items marked as done.\n"""
                    """-d (--done) <pattern>\tDisplays items matching"""
                    """ <pattern> as done.\n"""
                    """-D (--undone) <pattern>\tDisplays items matching"""
                    """ <pattern> as not done.\n"""
                    """--no-color\t\tDo not add color codes to the output.\n"""
                    """\nAdditional options:\n"""
                    """  -h (--help)\t\tShows this screen."""
                )
            elif arg == "m" or arg == "modify":
                self._part("modify", self.arg.modify, {
                    "-s": ("sort", True), "--sort": ("sort", True),
                    "-p": ("purge", False), "--purge": ("purge", False),
                    "-d": ("done", True), "--done": ("done", True),
                    "-D": ("undone", True), "--undone": ("undone", True)
                },
                    """Usage: td m [-h (--help)] [command(s)]"""
                    """, where [command(s)] are any of:\n\n"""
                    """-s (--sort) <pattern>\tSorts database using"""
                    """ <pattern>.\n"""
                    """-p (--purge)\t\tRemoves items marked as done.\n"""
                    """-d (--done) <pattern>\tMarks items matching"""
                    """ <pattern> as done.\n"""
                    """-D (--undone) <pattern>\tMarks items matching"""
                    """ <pattern> as not done.\n"""
                    """\nAdditional options:\n"""
                    """  -h (--help)\t\tShows this screen."""
                )
            elif arg == "a" or arg == "add":
                args = dict()
                if self.argv and self.arg.model.exists(self.argv[0]):
                    args["parent"] = self.argv.popleft()
                self._part("add", self.arg.add, {
                    "-n": ("name", True), "--name": ("name", True),
                    "-p": ("priority", True), "--priority": ("priority", True),
                    "-c": ("comment", True), "--comment": ("comment", True)
                },
                    """Usage: td a [-h (--help)] [parent] [command(s)]"""
                    """, where [command(s)] are any of:\n\n"""
                    """-n (--name) <text>\t\tSets item's name.\n"""
                    """-p (--priority) <no|name>\tSets item's priority.\n"""
                    """-c (--comment) <text>\t\tSets item's comment.\n"""
                    """\nIf [parent] index is specified, new item will"""
                    """ become it's child.\n"""
                    """If any of the arguments is omitted,"""
                    """ this command will launch an interactive session"""
                    """ letting the user supply the rest of them.\n"""
                    """\nAdditional options:\n"""
                    """  -h (--help)\t\t\tShows this screen.""",
                    **args
                )
            elif arg == "e" or arg == "edit":
                if not self.argv:
                    raise NotEnoughArgumentsError("edit")
                args = dict()
                if self.argv[0] not in ["-h", "--help"]:
                    args["index"] = self.argv.popleft()
                self._part("edit", self.arg.edit, {
                    "--parent": ("parent", True),
                    "-n": ("name", True), "--name": ("name", True),
                    "-p": ("priority", True), "--priority": ("priority", True),
                    "-c": ("comment", True), "--comment": ("comment", True)
                },
                    """Usage: td e [-h (--help)] <index> [command(s)]"""
                    """, where [command(s)] are any of:\n\n"""
                    """--parent <index>\t\tChanges item's parent.\n"""
                    """-n (--name) <text>\t\tChanges item's name.\n"""
                    """-p (--priority) <no|name>\tChanges item's priority.\n"""
                    """-c (--comment) <text>\t\tChanges item's comment.\n"""
                    """\nIndex argument is required and has to point at"""
                    """ an existing item.\n"""
                    """If any of the arguments is omitted, it will launch"""
                    """ an interactive session letting the user supply the"""
                    """ rest of them.\n"""
                    """\nAdditions options:\n"""
                    """  -h (--help)\t\t\tShows this screen.""",
                    **args
                )
            elif arg == "r" or arg == "rm":
                args = dict()
                if not self.argv:
                    raise NotEnoughArgumentsError("rm")
                elif self.argv[0] not in ["-h", "--help"]:
                    args["index"] = self.argv.popleft()
                self._part("rm", self.arg.rm, {
                },
                    """Usage: td r [-h (--help)] <index>\n\n"""
                    """Index argument is required and has to point at"""
                    """ an existing item.\n"""
                    """\nAdditions options:\n"""
                    """  -h (--help)\tShows this screen.""",
                    **args
                )
            elif arg == "d" or arg == "done":
                args = dict()
                if not self.argv:
                    raise NotEnoughArgumentsError("done")
                elif self.argv[0] not in ["-h", "--help"]:
                    args["index"] = self.argv.popleft()
                self._part("done", self.arg.done, {
                },
                    """Usage: td d [-h (--help)] <index>\n\n"""
                    """Index argument is required and has to point at"""
                    """ an existing item.\n"""
                    """\nAdditional options:\n"""
                    """  -h (--help)\tShows this screen.""",
                    **args
                )
            elif arg == "D" or arg == "undone":
                args = dict()
                if not self.argv:
                    raise NotEnoughArgumentsError("undone")
                elif self.argv[0] not in ["-h", "--help"]:
                    args["index"] = self.argv.popleft()
                self._part("undone", self.arg.undone, {
                },
                    """Usage: td D [-h (--help)] <index>\n\n"""
                    """Index argument is required and has to point at"""
                    """ an existing item.\n"""
                    """\nAdditional options:\n"""
                    """  -h (--help)\tShows this screen.""",
                    **args
                )
            elif arg == "o" or arg == "options":
                self._part("options", self.arg.options, {
                    "-g": ("glob", False), "--global": ("glob", False),
                    "-s": ("sort", True), "--sort": ("sort", True),
                    "-p": ("purge", False), "--purge": ("purge", False),
                    "-d": ("done", True), "--done": ("done", True),
                    "-D": ("undone", True), "--undone": ("undone", True)
                },
                    """Usage: td o [-h (--help)] [command(s)]"""
                    """, where [command(s)] are any of:\n\n"""
                    """-g (--global)\t\tApply specified options to all"""
                    """ ToDo lists (store in ~/.tdrc).\n"""
                    """-s (--sort) <pattern>\tAlways sorts using"""
                    """ <pattern>.\n"""
                    """-p (--purge)\t\tAlways removes items marked"""
                    """as done.\n"""
                    """-d (--done) <pattern>\tAlways marks items maching"""
                    """ <pattern> as done.\n"""
                    """-D (--undone) <pattern>\tAlways marks items maching"""
                    """ <pattern> as not done.\n"""
                    """\nAdditional options:\n"""
                    """  -h (--help)\t\tShows this screen."""
                )
            else:
                raise UnrecognizedCommandError("td", arg)


class Get(object):
    """Handles keyboard input."""

    TYPES = {
        "name": "any text (required)",
        "comment": "any text (<empty>)",
        "priority": "no/name (3/normal)",
        "parent": "index (<top level>)"
    }
    PRIORITIES = {
        "lowest": "1",
        "low": "2",
        "normal": "3",
        "high": "4",
        "highest": "5"
    }
    _LEN = 27

    def __init__(self):
        """Creates new Get instance.

        Also sets readline hook.

        """
        self.value = None
        readline.set_startup_hook(lambda: readline.insert_text(
            self.value is not None and str(self.value) or ""
        ))

    def input(self, field):
        """Gets user input for given field.

        Can be interrupted with ^C.

        :field: Field name.
        :returns: User input.

        """
        try:
            desc = Get.TYPES[field]
            return input("{}|{}[{}]> ".format(
                field, "-" * (Get._LEN - len(field) - len(desc)), desc
            ))
        except KeyboardInterrupt:
            print()
            exit(0)

    def get(self, field, value=None):
        """Gets user input for given field and checks if it is valid.

        If input is invalid, it will ask the user to enter it again.
        Defaults values to empty or :value:.

        It does not check validity of parent index. It can only be tested
        further down the road, so for now accept anything.

        :field: Field name.
        :value: Default value to use for field.
        :returns: User input.

        """
        self.value = value
        val = self.input(field)
        if field == 'name':
            while True:
                if val != '':
                    break
                print("Name cannot be empty.")
                val = self.input(field)
        elif field == 'priority':
            if val == '':  # Use default priority
                return None
            while True:
                if val in Get.PRIORITIES.values():
                    break
                c, val = val, Get.PRIORITIES.get(val)
                if val:
                    break
                print("Unrecognized priority number or name [{}].".format(c))
                val = self.input(field)
            val = int(val)
        return val


class Arg(object):
    """Main entry point.

    Handles patterns decoding and calling appropriate view/model manipulation
    methods. Also takes care of cmd arguments parsing, using Parser class.

    """

    def __init__(self, model):
        """Creates new Arg instance.

        :model: Model instance.

        """
        self.model = model
        Parser(self, sys.argv).rock()

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
            # REMEMBER: This False is for sort reverse!
            return ([(0, False)], {})

        def _getReverse(pm):
            return pm == '-'

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

    def _getDone(self, done, undone):
        """Parses the done|undone state.

        :done: Done marking pattern.
        :undone: Not done marking pattern.
        :returns: Pattern for done|undone or None if neither were specified.

        """
        if done:
            return self._getPattern(done, True)
        if undone:
            return self._getPattern(undone, False)

    def view(self, sort=None, purge=False, done=None, undone=None, **kwargs):
        """Handles the 'v' command.

        :sort: Sort pattern.
        :purge: Whether to purge items marked as 'done'.
        :done: Done pattern.
        :undone: Not done pattern.
        :kwargs: Additional arguments to pass to the View object.

        """
        View(self.model.modify(
            sort=self._getPattern(sort),
            purge=purge,
            done=self._getDone(done, undone)
        ), **kwargs)

    def modify(self, sort=None, purge=False, done=None, undone=None):
        """Handles the 'm' command.

        :sort: Sort pattern.
        :purge: Whether to purge items marked as 'done'.
        :done: Done pattern.
        :undone: Not done pattern.

        """
        self.model.modifyInPlace(
            sort=self._getPattern(sort),
            purge=purge,
            done=self._getDone(done, undone)
        )

    def add(self, **args):
        """Handles the 'a' command.

        :args: Arguments supplied to the 'a' command.

        """
        kwargs = self.getKwargs(args)
        if kwargs:
            self.model.add(**kwargs)

    def edit(self, **args):
        """Handles the 'e' command.

        :args: Arguments supplied to the 'e' command.

        """
        if self.model.exists(args["index"]):
            values = dict(zip(
                ['parent', 'name', 'priority', 'comment', 'done'],
                self.model.get(args["index"])
            ))
            kwargs = self.getKwargs(args, values)
            if kwargs:
                self.model.edit(args["index"], **kwargs)

    def rm(self, index):
        """Handles the 'r' command.

        :index: Index of the item to remove.

        """
        if self.model.exists(index):
            self.model.remove(index)

    def done(self, index):
        """Handles the 'd' command.

        :index: Index of the item to mark as done.

        """
        if self.model.exists(index):
            self.model.edit(index, done=True)

    def undone(self, index):
        """Handles the 'D' command.

        :index: Index of the item to mark as not done.

        """
        if self.model.exists(index):
            self.model.edit(index, done=False)

    def options(self, glob=False, **args):
        """Handles the 'o' command.

        :glob: Whether to store specified options globally.
        :args: Arguments supplied to the 'o' command (excluding '-g').

        """
        kwargs = {}
        for argname, argarg in args.items():
            if argname == "sort":
                argarg = self._getPattern(argarg)
            if argname not in ["done", "undone"]:
                kwargs[argname] = argarg
        if "done" in args or "undone" in args:
            kwargs["done"] = self._getDone(
                args.get("done"), args.get("undone")
            )

        self.model.setOptions(glob=glob, **kwargs)

    def getKwargs(self, args, values={}, get=Get()):
        """Gets necessary data from user input.

        :args: Dictionary of arguments supplied in command line.
        :values: Default values dictionary, supplied for editing.
        :get: Object used to get values from user input.
        :returns: A dictionary containing data gathered from user input.

        """
        kwargs = dict()
        for field in ['name', 'priority', 'comment', 'parent']:
            fvalue = args.get(field) or get.get(field, values.get(field))
            if fvalue is not None:
                kwargs[field] = fvalue
        return kwargs


def run():
    model = Model()
    Arg(model)
