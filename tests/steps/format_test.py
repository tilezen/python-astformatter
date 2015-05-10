from behave import *
from ASTFormatter import ASTFormatter
import ast
import sys

"""
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".
"""

try:
  "".decode
  def decode_escapes(s):
    return s.decode('string_escape')
except AttributeError:
  def decode_escapes(s):
    return bytes(s).decode('string_escape')

@given("I have parsed an AST tree from \"{source}\",")
def given_a_source_input_of(context, source):
    context.tree = ast.parse(decode_escapes(source)) 

@when("I transform the AST tree to source,")
def when_I_transform_the_tree_to_source(context):
    context.formatted = ASTFormatter().format(context.tree)

@then("the output should include \"{output}\".")
def then_the_output_should_include(context, output):
    assert decode_escapes(output) in context.formatted, ("%r not in %r" % (output, context.formatted))
