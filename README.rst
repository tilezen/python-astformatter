ASTFormatter
============

The ASTFormatter class accepts an AST tree and returns a valid source code representation of that tree.

Example Usage
-------------

::

    from astformatter import ASTFormatter
    import ast

    tree = ast.parse(open('modulefile.py'), 'modulefile.py', mode='exec')
    src  = ASTFormatter().format(tree, mode='exec')

Bugs
----

- Currently, indentation is fixed at 4 spaces.

- Too many methods are exposed that shouldn't be, in order to properly subclass `ast.NodeVisitor`.

- Need to make the statement visitor methods consistent about returning a list of strings; most still just return a string.

- Code modified to work with 3.x needs cleanup

Latest Changes
--------------

version 0.6.2
  Add missing newlines for two uses of ``raise``

Copyright
---------

Copyright |copy| 2015-2016 by Johnson Earls.  Some rights reserved.  See the license_ for details.

.. _license: https://raw.githubusercontent.com/darkfoxprime/python-astformatter/master/LICENSE
.. |copy| unicode:: 0xA9 .. copyright sign
