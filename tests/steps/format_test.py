from behave import *
from ASTFormatter import ASTFormatter
import ast

"""
        Given I have parsed an AST tree from "<source input>",
         when I transform the AST tree to source,
         then the output should include "<output snippet>".
"""

@given("I have parsed an AST tree from \"{source}\",")
def given_a_source_input_of(context, source):
    context.tree = ast.parse(source.decode('string_escape')) 

@when("I transform the AST tree to source,")
def when_I_transform_the_tree_to_source(context):
    context.formatted = ASTFormatter().format(context.tree)

@then("the output should include \"{output}\".")
def then_the_output_should_include(context, output):
    assert output.decode('string_escape') in context.formatted, ("%r not in %r" % (output, context.formatted))
