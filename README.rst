ASTFormatter
============

The ASTFormatter class accepts an AST tree and returns a valid source code representation of that tree.

Example Usage
-------------

::

    from ASTFormatter import ASTFormatter
    import ast
    
    tree = ast.parse(open('modulefile.py'), 'modulefile.py', mode='exec')
    src  = ASTFormatter.format(tree, mode='exec')

Bugs
----

- Currently, indentation is fixed at 4 spaces.

- Too many methods are exposed that shouldn't be, in order to properly subclass `ast.NodeVisitor`.

- Need to make the statement visitor methods consistent about returning a list of strings; most still just return a string.

- Not tested with Python 3.0 at all.

Copyright
---------

Copyright |copy| 2015 by Johnson Earls.  Some rights reserved.  See the license for details.

.. |copy| unicode:: 0xA9 .. copyright sign
