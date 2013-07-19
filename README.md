**td** is a non-offensive, per project ToDo manager.

Heavily inspired by [devtodo][devtodo], but with some nasty features, like:

* Shorter commands for most used actions.
* Sorting/Filtering specific levels only.
* Persistent sort/filter/view options.
* Written in pure Python (it even has docstrings).
* Tests ([![Build Status](https://travis-ci.org/KenjiTakahashi/td.png?branch=master)](https://travis-ci.org/KenjiTakahashi/td) [![Coverage](https://coveralls.io/repos/KenjiTakahashi/td/badge.png?branch=master)](https://coveralls.io/r/KenjiTakahashi/td)).

Oh, and it will automagically pick up your existing [devtodo][devtodo] lists!

## screenshot
![screenshot](http://dl.dropbox.com/u/20714377/td.png)

## requirements
* python3
* distribute (for setup)
* nosetests (for test-suite)

## installation

Through [PyPI][pypi]
```sh
$ pip install td
```
or from sources
```sh
$ python setup.py install
```

## usage

#### show
To show your complete ToDo list, just run **td** without any parameters.
```sh
$ td
```

#### add
Typing
```sh
$ td a(dd) [<parent index>]
```
will start an interactive item adding session.

Optional *parent_index* parameter specifies item, under which the new one will be nested.

Instead of using interactive session, one can also specify them in command line, like below.
```sh
$ td a(dd) [<parent index>] --<field name> <field value>
$ td a(dd) [<parent index>] -<first letter of the field name> <field value>
```

#### edit
Typing
```sh
$ td e(dit) <index>
```
where *index* is an item's index, will start an interactive item editing session.

Similarly to **a(dd)**, one can also specify new values in command line.
```sh
$ td e(dit) <index> --<field name> <field value>
$ td e(dit) <index> -<first letter of the field name> <field value>
```
One special cause here is reparenting, done like below.
```sh
$ td e(dit) <index> --parent <parent index>
```

#### remove
Typing
```sh
$ td r(emove) <index>
```
will remove item under *index*.

#### done/undone
Typing
```sh
$ td d(one) <index>
```
will mark item under *index* as done, while typing
```sh
$ td D <index>
$ td undone <index>
```
will mark it as not done.

#### modify
Performs a one time modification of the list and saves it to disk.

**sort**

Used to sort items on the list.

General syntax is
```sh
$ td (v|m|o) -s [+|-]{,}[[<level>]{:}[<field_name>](+|-)]
$ td (v|m|o) --sort [+|-]{,}[[<level>]{:}[<field_name>](+|-)]
```
but it looks cryptic, so lets split it into some more specific use cases.

To sort everything ascending by name, type
```sh
$ td (v|m|o) -s
$ td (v|m|o) -s +
```
To sort everything descending by name, type
```sh
$ td (v|m|o) -s -
```
To sort specific level by name, type (as before, + goes for ascending and - for descending)
```sh
$ td (v|m|o) -s <level>(+|-)
```
To sort everything by a field other than name, type
```sh
$ td (v|m|o) -s <field name>(+|-)
```
To sort specific level by a field other than name, type
```sh
$ td (v|m|o) -s <level>:<field name>(+|-)
```
And to specify muliple rules, use a comma (`,`). For example this
```sh
$ td (v|m|o) -s +,1-,2:priority+
```
will sort items at the second level ascending by priority, item at the first level descending by name, and all other levels ascending by name.

Note that to sort by multiple conditions, just supply them one by one and they'll be applied in order of appearance.

**purge**

Typing
```sh
$ td (v|m|o) -p
$ td (v|m|o) --purge
```
will remove all completed items.

**done/undone**

Used to batch mark items as done or not.

General syntax is
```sh
$ td (v|m|o) -d [[<level>]{:}[[<field name>=]<regexp>]]
$ td (v|m|o) --done [[<level>]{:}[[<field name>=]<regexp>]]
```
```sh
$ td (v|m|o) -D [[<level>]{:}[[<field name>=]<regexp>]]
$ td (v|m|o) --undone [[<level>]{:}[[<field name>=]<regexp>]]
```
As with **sort**, we'll split it into use cases.

To mark all items, type
```sh
$ td (v|m|o) -(d|D)
```
To mark all items at specific level, type
```sh
$ td (v|m|o) -(d|D) <level>
```
To mark items matching regexp at *any* field and level, type
```sh
$ td (v|m|o) -(d|D) <regexp>
```
To mark items matching regexp at *specific* field and *any* level, type
```sh
$ td (v|m|o) -(d|D) <field name>=<regexp>
```
To mark items matching regexp at *any* field and *specific* level, type
```sh
$ td (v|m|o) -(d|D) <level>:<regexp>
```
To mark items matching regexp at *specific* field and level, type
```sh
$ td (v|m|o) -(d|D) <level>:<field name>=<regexp>
```
Of course, these rules can also be chained using comma (`,`).

#### view
Affects how the list is displayed on the screen. It does not modify the list physically and only takes effect for one run, all settings are then gone.

Shares the interface of `modify` command, with following additions.

**nocolor**

Disables any possible color codes, i.e. prints pure textual data. Might be useful for storing and/or reusing the output.

```sh
$ td v --no-color
```

#### options
Describes persistent options, which will be applied every next time **td** is run.

Shares the interface of `modify` command, with following additions.

**global**
Stores options globally (in `~/.tdrc`), which means that they will be applied to all lists.

**Note:** Local options take precedence over global ones.

```sh
$ td o -g <other options>
$ td o --global <other options>
```

[devtodo]: http://swapoff.org/devtodo1.html
[pypi]: https://pypi.python.org/pypi/td
