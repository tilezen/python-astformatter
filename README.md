# python-astformatter
The ASTFormatter class accepts an AST tree and returns a valid source code representation of that tree.

## Example Usage

    from ASTFormatter import ASTFormatter
    
    source = ASTFormatter().format(ast.parse(...,mode='exec'),mode='exec')

## Bugs

Currently, indentation is fixed at 4 spaces.

Too many methods are exposed that shouldn't be, in order to properly subclass `ast.NodeVisitor`.

Need to make the statement visitor methods consistent about returning a list of strings; most still just return a string.

Not tested with Python 3.0 at all.

## Copyright

Copyright &copy; 2015 by Johnson Earls.  Some rights reserved.  See the [LICENSE](LICENSE) for details.