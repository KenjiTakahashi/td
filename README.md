**td** is a non-offensive, per project ToDo manager.

Heavily inspired by [devtodo][devtodo], but with some nasty features, like:

* Shorter commands for most used actions.
* Sorting/Filtering specific levels only.
* Persistent sort/filter/view options.
* Written in pure Python (it even has docstrings).
* Tests ([![Build Status](https://travis-ci.org/KenjiTakahashi/td.png?branch=master)](https://travis-ci.org/KenjiTakahashi/td)).

Oh, and it will automagically pick up your existing [devtodo][devtodo] lists!

## screenshot
![screenshot](http://dl.dropbox.com/u/20714377/td.png)

## requirements
* python >= 3.2
* colorama
* distribute (for setup)
* nosetests (for test-suite)

## usage
#### show
To show your complete ToDo list, just run **td** without any parameters.
```sh
$ td
```
#### add
Typing
```sh
$ td a(dd) [<parent_index>]
```
will start an interactive item adding session.

Optional *parent_index* parameter specifies item, under which the new one will be nested.

Instead of using interactive session, one can also specify them in command line, like below.
```sh
$ td a(dd) [<parent_index>] --<field_name> <field_value>
$ td a(dd) [<parent_index>] -<field_name's_first_letter> <field_value>
```
#### edit
Typing
```sh
$ td e(dit) <index>
```
where *index* is an item's index, will start an interactive item editing session.

Similarly to **a(dd)**, one can also specify new values in command line.
```sh
$ td e(dit) <index> --<field_name> <field_value>
$ td e(dit) <index> -<field_name's_first_letter> <field_value>
```
One special cause here is reparenting, done like below.
```sh
$ td e(dit) <index> --parent <parent_index>
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
#### view/modify/options
All view, modify and options commands have exactly the same interface, but:

* v(iew) is temporary, which means that changes affect only one session and are then gone,
* m(odify) is permanent, which means that the changes made are saved to disk,
* o(ptions) sets persistent modifiers, which will be applied on every future change.

**sort**

General syntax is
```sh
$ td (v|m|o) -s [+|-]{,}[[<level>]{:}[<field_name>](+|-)]
$ td (v|m|o) --sort [+|-]{,}[[<level>]{:}[<field_name>](+|-)]
```
but it looks cryptic, so lets split it into some more specific use cases.

To sort everything asceding by name, type
```sh
$ td (v|m|o) -s
$ td (v|m|o) -s +
```
To sort everything desceding by name, type
```sh
$ td (v|m|o) -s -
```
To sort specific level by name, type (as before, + goes for asceding and - for desceding)
```sh
$ td (v|m|o) -s <level>(+|-)
```
To sort everything by a field other than name, type
```sh
$ td (v|m|o) -s <field_name>(+|-)
```
To sort specific level by a field other than name, type
```sh
$ td (v|m|o) -s <level>:<field_name>(+|-)
```
And to specify muliple rules, use a comma (`,`). For example this
```sh
$ td (v|m|o) -s +,1-,2:priority+
```
will sort items at the second level asceding by priority, item at the first level desceding by name, and all other levels asceding by name.

**purge**

Typing
```sh
$ td (v|m|o) -p
$ td (v|m|o) --purge
```
will remove all completed items.

**done/undone**

This command is used to batch mark items as done or not.

General syntax is
```sh
$ td (v|m|o) -d [[<level>]{:}[[<field_name>=]<regexp>]]
$ td (v|m|o) --done [[<level>]{:}[[<field_name>=]<regexp>]]
```
```sh
$ td (v|m|o) -D [[<level>]{:}[[<field_name>=]<regexp>]]
$ td (v|m|o) --undone [[<level>]{:}[[<field_name>=]<regexp>]]
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
$ td (v|m|o) -(d|D) <field_name>=<regexp>
```
To mark items matching regexp at *any* field and *specific* level, type
```sh
$ td (v|m|o) -(d|D) <level>:<regexp>
```
To mark items matching regexp at *specific* field and level, type
```sh
$ td (v|m|o) -(d|D) <level>:<field_name>=<regexp>
```
Of course, these rules can also be chained using comma (`,`).

[devtodo]: http://swapoff.org/devtodo1.html
