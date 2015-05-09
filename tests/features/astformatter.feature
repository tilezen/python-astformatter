Feature: Generate proper Python code
    In order to be able to transform and recreate Python modules,
    as a software developer,
    I want the ASTFormatter class to be able to generate proper
    Python code for any given AST tree.

    Scenario Outline: Basic AST structures should work.
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | def foo(x): pass                                      | def foo(x):\n    pass                                     |
        | class foo(object): pass                               | class foo(object):                                        |
        | return x                                              | return x                                                  |
        | del foo[0]                                            | del foo[0]                                                |
        | foo = x                                               | foo = x                                                   |
        | foo += y                                              | foo += y                                                  |
        | print >> foo, x,                                      | print >> foo, x,                                          |
        | for target in (1,2,3):\n  pass\nelse:\n  pass         | for target in (1, 2, 3):\n    pass\nelse:\n    pass       |
        | while foo:\n  pass\nelse:\n  pass                     | while foo:\n    pass\nelse:\n    pass                     |
        | if foo:\n  pass\nelif foo:\n  pass\nelse:\n  pass     | if foo:\n    pass\nelif foo:\n    pass\nelse:\n    pass   |
        | with foo as x:\n  pass                                | with foo as x:\n    pass                                  |
        | raise foo,x                                           | raise foo,x                                               |
        | try:\n  pass\nexcept foo,x:\n  pass\nelse:\n  pass    | try:\n    pass\nexcept foo,x:\n    pass\nelse:\n    pass  |
        | try:\n  pass\nfinally:\n  pass                        | try:\n    pass\nfinally:\n    pass                        |
        | assert foo,x                                          | assert foo,x                                              |
        | import foo,bar as x                                   | import foo\nimport bar as x                               |
        | from foo import bar as x                              | from foo import bar as x                                  |
        | from foo import *                                     | from foo import *                                         |
        | from .foo import x                                    | from .foo import x                                        |
        | exec "foo" in x,y                                     | exec 'foo' in x, y                                        |
        | global foo, x                                         | global foo,x                                              |
        | foo                                                   | foo                                                       |
        | pass                                                  | pass                                                      |
        | break                                                 | break                                                     |
        | continue                                              | continue                                                  |
        | x and y                                               | x and y                                                   |
        | x or y                                                | x or y                                                    |
        | x or y or z                                           | x or y or z                                               |
        | x + y                                                 | x + y                                                     |
        | x - y                                                 | x - y                                                     |
        | x * y                                                 | x * y                                                     |
        | x / y                                                 | x / y                                                     |
        | x % y                                                 | x % y                                                     |
        | x ** y                                                | x ** y                                                    |
        | x << y                                                | x << y                                                    |
        | x >> y                                                | x >> y                                                    |
#       | x | y                                                 | x | y                                                     |
        | x & y                                                 | x & y                                                     |
        | x // y                                                | x // y                                                    |
        | +x                                                    | + x                                                       |
        | -x                                                    | - x                                                       |
        | ~x                                                    | ~ x                                                       |
        | lambda foo: x                                         | lambda foo: x                                             |
        | foo if x else y                                       | foo if x else y                                           |
        | { foo: x, bar: y }                                    | {foo:x, bar:y}                                            |
        | [ foo for foo in x if y ]                             | [foo for foo in x if y]                                   |
        | ( foo for foo in x if y )                             | (foo for foo in x if y)                                   |
        | yield foo                                             | yield foo                                                 |
        | foo < x                                               | foo < x                                                   |
        | foo < x < y                                           | foo < x < y                                               |
        | y > x                                                 | y > x                                                     |
        | x == y                                                | x == y                                                    |
        | x != y                                                | x != y                                                    |
        | x <> y                                                | x != y                                                    |
        | x <= y                                                | x <= y                                                    |
        | x >= y                                                | x >= y                                                    |
        | x is y                                                | x is y                                                    |
        | x is not y                                            | x is not y                                                |
        | x in y                                                | x in y                                                    |
        | x not in y                                            | x not in y                                                |
        | foo(x, y=1, *z, **q)                                  | foo(x, y=1, *z, **q)                                      |
        | `foo`                                                 | `foo`                                                     |
        | 123                                                   | 123                                                       |
        | foo = "foo"                                           | foo = 'foo'                                               |
        | foo = 'foo'                                           | foo = 'foo'                                               |
        | foo = """foo\nbar"""                                  | foo = 'foo\\nbar'                                         |
        | "foo"                                                 | """foo"""                                                 |
        | 'bar"""baz'                                           | """bar\\"\\"\\"baz"""                                     |
        | """quux\nfoobar"""                                    | """quux\nfoobar\n"""                                      |
        | foo.x                                                 | foo.x                                                     |
        | foo[x]                                                | foo[x]                                                    |
        | foo[x:y:z]                                            | foo[x:y:z]                                                |
        | [x,y,z]                                               | [x, y, z]                                                 |
        | (x,y,z)                                               | (x, y, z)                                                 |

    Scenario Outline: Operator precedence should be taken into account
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".

    Examples:
        | source input                                          | output snippet                                            |
        | x + y * z                                             | x + y * z                                                 |
        | (x + y) * z                                           | (x + y) * z                                               |
        | x + (y * z)                                           | x + y * z                                                 |