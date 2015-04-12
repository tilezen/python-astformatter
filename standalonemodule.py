# Requires: Python 2.6
# Author:   Johnson Earls
# Version:  0.0.0
# URL:      https://raw.githubusercontent.com/darkfoxprime/python-makestandalone/
'''This module provides the StandaloneModule class, which can help with
incorporating local library modules into an application module to create
stand-alone module.
'''

########################################################################
# system libraries
import sys
# !!! check minimum version immediately
if (
        sys.version_info[0] < 2 or
        sys.version_info[1] < 6 or
        sys.version_info[0] > 2):
    raise RuntimeError("standalonemodule requires Python 2.6 or better")
# rest of system libraries (that might only exist in required version)
import ast
import os.path
import re

########################################################################
# 3rd party libraries
# (if any)

########################################################################
# local libraries
# (if any)

########################################################################

__all__ = ['StandaloneModule']

########################################################################
# define some internal clases needed for the StandaloneModule class to
# work

########################################################################
# The ImportNodeTransformer processes import nodes and, if needed,
# replaces them with their wrapped content.

class ImportNodeTransformer(ast.NodeTransformer):
    def __init__(self, importPath=[]):
        self._importPath = importPath
    def visit_Import(self,node):
        replacementNodes = [
            self._processNode(
                alias.name,
                module_as=alias.asname,
                lineno=node.lineno,
                charno=node.col_offset
            ) for alias in node.names
        ]
        return replacementNodes
    def visit_ImportFrom(self,node):
        replacementNodes = [
            self._processNode(
                self.module,
                import_names=[(alias.name, alias.asname) for alias in node.names],
                relative_level=node.level,
                lineno=node.lineno,
                charno=node.col_offset
            )
        ]
        return replacementNodes

    def _processNode(
            self, module, module_as = None,
            import_names = None, relative_level = None,
            lineno = None, charno = None):
        print "importing module %s(%s) names %s level %s location %s:%s" % (repr(module), repr(module_as), repr(import_names), repr(relative_level), repr(lineno), repr(charno))
        if import_names is None:
            if module_as is None:
                module_as = module
            return ast.Import(ast.alias(module, module_as), lineno=lineno, col_offset=charno)
        else:
            return ast.ImportFrom(module, [ast.alias(name, asname) for (name,asname) in import_names], relative_level, lineno=lineno, col_offset=charno)

########################################################################
# The ASTFormatter class walks an AST and produces properly formatted
# python code for that AST.

class ASTFormatter(ast.NodeVisitor):
    def __init__(self):
        self.context = [ast.Module]
        self.indent = 0

    ####################################################################
    # helper methods

    def process_body(self, stmtlist, indent=""):
        self.indent = len(indent)
        content = []
        for stmt in stmtlist:
            self.context.insert(0, stmt.__class__)
            stmts = self.visit(stmt)
            if not isinstance(stmts,list):
                stmts = [stmts]
            content += ["%s%s" % (indent, stmt) for stmt in stmts]
        return content

    def process_child(self, nodelist):
        if not isinstance(nodelist,(list,tuple)):
            nodelist = [nodelist]
        return [self.visit(node) for node in nodelist]
    def flatten_one(self,deeplist):
        retval = []
        for item in deeplist:
            if isinstance(item,list):
                retval.extend(item)
            else:
                retval.append(item)
        return retval

    seenTypes = set()

    def generic_visit(self,node):
        if type(node) not in self.seenTypes:
            print >> sys.stderr, repr(node)
            self.seenTypes.add(type(node))
        try:
            children = "(%s)" % (",".join(self.flatten_one([self.process_child(getattr(node,field)) for field in node._fields])),)
        except AttributeError:
            children = ""
        if isinstance(node,ast.stmt):
            return "#%s#%s\n" % (node.__class__.__name__, children)
        # should be an expr at this point?
        return "#%s#%s" % (node.__class__.__name__, children)

    ####################################################################
    # expression methods - these return a single string with no newline

    def visit_alias(self, node):
        if node.asname is None:
            return node.name
        else:
            return "%s as %s" % (node.name, node.asname)

    def visit_Add(self,node):
        return "+"

    def visit_And(self,node):
        return "and"

    def visit_arguments(self,node):
        args = ["%s" % (self.visit(arg),) for arg in node.args[:-len(node.defaults)]]
        defargs = ["%s=%s" % (self.visit(arg), self.visit(default)) for (arg,default) in zip(node.args[-len(node.defaults):], node.defaults)]
        if node.vararg:
            vararg = ["*" + self.visit(node.vararg)]
        else:
            vararg = []
        if node.kwarg:
            kwarg = ["**" + self.visit(node.kwarg)]
        else:
            kwarg = []
        return "(%s)" % (",".join(args + defargs + vararg + kwarg),)

    def visit_Attribute(self,node):
        return "%s.%s" % (self.visit(node.value), node.attr)

    def visit_BinOp(self,node):
        return "%s %s %s" % (self.visit(node.left), self.visit(node.op), self.visit(node.right))

    def visit_BitAnd(self,node):
        return "&"

    def visit_BitOr(self,node):
        return "|"

    def visit_BitXor(self,node):
        return "^"

    def visit_BoolOp(self,node):
        op = self.visit(node.op)
        return (" %s " % (op,)).join([self.visit(value) for value in node.values])

    def visit_Call(self,node):
        args = [self.visit(arg) for arg in node.args]
        keywords = [self.visit(keyword) for keyword in node.keywords]
        if node.starargs:
            starargs = ["*%s" % (self.visit(node.starargs),)]
        else:
            starargs = []
        if node.kwargs:
            kwargs = ["**%s" % (self.visit(node.kwargs),)]
        else:
            kwargs = []
        return "%s(%s)" % (self.visit(node.func), ", ".join(args + keywords + starargs + kwargs))

    def visit_Compare(self,node):
        return "%s %s" % (self.visit(node.left), " ".join(["%s %s" % (self.visit(op),self.visit(right)) for (op,right) in zip(node.ops, node.comparators)]))

    def visit_comprehension(self,node):
        ifs = "".join([" if %s" % (self.visit(ifpart),) for ifpart in node.ifs])
        return "for %s in %s%s" % (self.visit(node.target), self.visit(node.iter), ifs)

    def visit_Dict(self,node):
        return "{%s}" % (", ".join(["%s:%s" % (self.visit(key), self.visit(value)) for (key,value) in zip(node.keys, node.values)]),)

    def visit_Div(self,node):
        return "/"

    def visit_Ellipsis(self,node):
        return "..."

    def visit_Eq(self,node):
        return "=="

    def visit_ExtSlice(self,node):
        return ", ".join([self.visit(dim) for dim in node.dims])

    def visit_FloorDiv(self,node):
        return "//"

    def visit_GeneratorExp(self,node):
        if node.generators:
            return "(%s %s)" % (self.visit(node.elt), " ".join(self.visit(generator) for generator in node.generators),)
        return "(%s)" % (self.visit(node.elt),)

    def visit_Gt(self,node):
        return ">"

    def visit_GtE(self,node):
        return ">="

    def visit_IfExp(self,node):
        return "%s if %s else %s" % (self.visit(node.body), self.visit(node.test), self.visit(node.orelse))

    def visit_In(self,node):
        return "in"

    def visit_Index(self,node):
        return self.visit(node.value)

    def visit_Invert(self,node):
        return "~"

    def visit_Is(self,node):
        return "is"

    def visit_IsNot(self,node):
        return "is not"

    def visit_keyword(self,node):
        return "%s=%s" % (node.arg, self.visit(node.value))

    def visit_Lambda(self,node):
        return "lambda %s:%s" % (self.visit(node.args), self.visit(node.body))

    def visit_List(self,node):
        return "[%s]" % (", ".join([self.visit(elt) for elt in node.elts]),)

    def visit_ListComp(self,node):
        if node.generators:
            return "[%s %s]" % (self.visit(node.elt), " ".join(self.visit(generator) for generator in node.generators),)
        return "[%s]" % (self.visit(node.elt),)

    def visit_Lt(self,node):
        return "<"

    def visit_LtE(self,node):
        return "<="

    def Visit_LShift(self,node):
        return "<<"

    def visit_Mod(self,node):
        return "%"

    def visit_Mult(self,node):
        return "*"

    def visit_Name(self,node):
        return node.id

    def visit_Not(self,node):
        return "not"

    def visit_NotEq(self,node):
        return "!="

    def visit_NotIn(self,node):
        return "not in"

    def visit_Num(self,node):
        return repr(node.n)

    def visit_Or(self,node):
        return "or"

    def visit_Pow(self,node):
        return "**"

    def visit_Repr(self,node):
        return "repr(%s)" % (self.visit(node.value),)

    def visit_RShift(self,node):
        return ">>"

    def visit_Slice(self,node):
        if node.lower:
            lower = self.visit(node.lower)
        else:
            lower = ""
        if node.upper:
            upper = self.visit(node.upper)
        else:
            upper = ""
        if node.step:
            return ":".join([lower, upper, self.visit(node.step)])
        else:
            return ":".join([lower, upper])

    re_docstr_escape = re.compile(r'([\\"])')
    re_docstr_remove_blank_front = re.compile(r'^[ \n]*')
    re_docstr_remove_blank_back = re.compile(r'[ \n]*$')
    re_docstr_indent = re.compile(r'^( *).*')
    def visit_Str(self, node):
        if self.context[0] == ast.Expr:
            # process docstring
            docstring = self.re_docstr_remove_blank_front.sub('',
                    self.re_docstr_remove_blank_back.sub('',
                            self.re_docstr_escape.sub(r'\\\1', node.s))).split('\n')
            if len(docstring) > 1:
                docstr_indents = [
                    len(self.re_docstr_indent.sub(r'\1',ds)) for ds in [
                        ds.rstrip() for ds in docstring[1:]
                    ] if ds
                ]
                docstr_indent = min(docstr_indents)
                docstring = docstring[0:1] + ["%*s%s" % (self.indent, "", ds[docstr_indent:]) for ds in docstring[1:]]
            return '"""(docstring omitted"""' # return '"""%s\n"""' % ("\n".join(docstring),)
        else:
            return repr(node.s)

    def visit_Sub(self,node):
        return "-"

    def visit_Subscript(self,node):
        return "%s[%s]" % (self.visit(node.value), self.visit(node.slice))

    def visit_Tuple(self,node):
        if len(node.elts) == 1:
            return "(%s,)" % (self.visit(node.elts[0]),)
        return "(%s)" % (", ".join([self.visit(elt) for elt in node.elts]),)

    def visit_UAdd(self,node):
        return "+"

    def visit_USub(self,node):
        return "-"

    def visit_UnaryOp(self,node):
        return "%s %s" % (self.visit(node.op), self.visit(node.operand))

    def visit_Yield(self,node):
        if node.value:
            return "yield %s" % (self.visit(node.value),)
        return "yield"

    ####################################################################
    # statement methods - these return either a single string or a list
    # of strings, all terminated with a `\n` newline.

    def visit_Assert(self, node):
        if node.msg is not None:
            msg = "," + self.visit(node.msg)
        return "assert %s%s\n" % (self.visit(node.test), msg)

    def visit_Assign(self, node):
        return "%s = %s\n" % (",".join([self.visit(target) for target in node.targets]), self.visit(node.value))

    def visit_AugAssign(self, node):
        return "%s %s= %s\n" % (self.visit(node.target), self.visit(node.op), self.visit(node.value))

    def visit_Break(self,node):
        return "break\n"

    def visit_ClassDef(self,node):
        decorators = [self.visit(dec) for dec in node.decorator_list]
        supers = node.bases
        if supers is None or len(supers) == 0:
            supers = ""
        else:
            supers = "(%s)" % (", ".join([self.visit(super_) for super_ in supers]))
        classdef = ["class %s%s:\n" % (node.name, supers)]
        classbody = self.process_body(node.body, "    ")
        return decorators + classdef + classbody

    def visit_Continue(self,node):
        return "continue\n"

    def visit_Delete(self, node):
        return "del %s\n" % (",".join([self.visit(target) for target in node.targets]),)

    def visit_ExceptHandler(self,node):
        if not node.type:
            return ["except:\n"] + self.process_body(node.body, "    ")
        if node.name:
            return ["except %s,%s:\n" % (self.visit(node.type), self.visit(node.name))] + self.process_body(node.body, "    ")
        return ["except %s:\n" % (self.visit(node.type),)] + self.process_body(node.body, "    ")

    def visit_Exec(self,node):
        inglobals, inlocals = "", ""
        if self.inglobals is not None:
            inglobals = " in %s" % (self.visit(node.globals),)
            if self.inlocals is not None:
                inlocals = ", %s" % (self.visit(node.locals),)
        return "exec %s%s%s\n" % (self.visit(node.body), inglobals, inlocals)

    def visit_Expr(self,node):
        return self.visit(node.value) + "\n"

    def visit_For(self,node):
        if node.orelse is None or len(node.orelse) == 0:
            orelse = []
        else:
            orelse = ["else:\n"] + self.process_body(node.orelse, "    ")
        return [
            "for %s in %s:\n" % (
                self.visit(node.target),
                self.visit(node.iter),
            )
        ] + self.process_body(node.body, "    ") + orelse

    def visit_FunctionDef(self,node):
        decorators = [self.visit(dec) for dec in node.decorator_list]
        funcdef = ["def %s%s:\n" % (node.name, self.visit(node.args))]
        funcbody = self.process_body(node.body, "    ")
        return decorators + funcdef + funcbody

    def visit_Global(self,node):
        return "global %s\n" % (",".join([self.visit(name) for name in node.names]),)

    def visit_If(self,node):
        content = ["if %s:\n" % (self.visit(node.test),)] + self.process_body(node.body, "    ")
        if node.orelse is not None and len(node.orelse) > 0:
            content.extend(["else:\n"] + self.process_body(node.orelse, "    "))
        return content

    def visit_Import(self,node):
        return "import %s\n" % (self.visit(node.names),)

    def visit_Module(self,node):
        return self.process_body(node.body)

    def visit_Pass(self,node):
        return "pass\n"

    def visit_Print(self,node):
        if node.dest is None:
            dest = ""
        else:
            dest = ">> %s, " % (self.visit(node.dest),)
        if node.nl:
            nl = ""
        else:
            nl = ","
        return "print %s%s%s\n" % (dest, ", ".join([self.visit(value) for value in node.values]), nl)

    def visit_Raise(self,node):
        if node.tback is not None:
            params = (node.type, node.inst, node.tback)
        elif node.inst is not None:
            params = (node.type, node.inst)
        elif node.type is not None:
            params = (node.type,)
        else:
            params = ""
        if len(params):
            params = " " + ",".join([self.visit(param) for param in params])
        return "raise%s\n" % (params,)

    def visit_Return(self,node):
        if node.value is not None:
            return "return %s\n" % (self.visit(node.value),)
        return "return\n"

    def visit_TryExcept(self,node):
        retval = ["try:\n"] + self.process_body(node.body, "    ")
        for handler in node.handlers:
            retval.extend(self.visit(handler))
        if node.orelse is not None and len(node.orelse) > 0:
            retval.extend(["else:\n"] + self.process_body(node.orelse, "    "))
        return retval

    def visit_TryFinally(self,node):
        return ["try:\n"] + self.process_body(node.body, "    ") + ["finally:\n"] + self.process_body(node.finalbody, "    ")

    def visit_While(self,node):
        if node.orelse is None or len(node.orelse) == 0:
            orelse = []
        else:
            orelse = ["else:\n"] + self.process_body(node.orelse, "    ")
        return [
            "while %s:\n" % (
                self.visit(node.test),
            )
        ] + self.process_body(node.body, "    ") + orelse

    def visit_With(self,node):
        if node.optional_vars is None:
            asvars = ""
        else:
            asvars = " as %s" % (self.visit(node.optional_vars),)
        return [
            "with %s%s:\n" % (self.visit(node.context_expr),asvars)
        ] + self.process_body(node.body, "    ")

########################################################################
# the real StandaloneModule class:

class StandaloneModule(object):
    '''Process a module file to allow for incorporation of imported modules.
    
    An instance of this class is created with a module pathname and, optionally,
    an import path.  The instance will load and parse the module and locate all
    imports within it. The following methods are provided:

    *   `getImports` provides a list of those imports and associated file data.

    *   `getWarnings` provides a list of warnings about conflicts between import
        and non-import statements.
    
    *   `replaceImport` replaces the given import statement with text.

    *   `wrapContents` returns the contents of the module wrapped in a class
        definition, with local name bindings to the wrapped contents.

    *   `generateBindings` just returns the bindings for the module.

    The single method `createStandalone` wraps all of these up into one call and
    recursively applies itself to the imported modules themselves as well.

    Simple Usage:
    
        print StandaloneModule(
            "myclass.py",
            importPath=["lib"]
        ).createStandalone()

    To do that by hand:
    
        def createStandalone(moduleFilename,importPath=[]):
            # BUG: This does not handle multiple imports of the same module
            thisModule = StandaloneModule(moduleFilename, importPath)
            # print warnings first
            for warning in thisModule.getWarnings():
                print >> sys.stderr, (
                        "Warning: Import of %(importModule)s coexists "
                        "with another statement on line %(importLine)d "
                        "of file %(fromFile)s.  The other statements will "
                        "be deleted by this import!"
                    ) % warning
            imports = thisModule.getImports()
            # get the list of imports, reverse-sorted by first line number:
            for import_ in [
                import_ for (import_,info) in sorted(
                    imports.items(),
                    key=lambda (import_,info):sorted(info['names'].keys())[0],
                    reverse=True
                )
            ]:
                newModule = createStandalone(imports[import_]['filename'],importPath)
                firstImport = True
                for lineno in sorted(import_['names'].keys()):
                    if firstImport:
                        thisModule.replaceLine(
                            lineno,
                            newModule.wrapContents(
                                className='__imported_%s' % (import_.replace('.','_'),),
                                importNames = import_['names'],
                                indentLevel=4
                            )
                        )
                    else:
                        thisModule.replaceLine(
                            lineno,
                            newModule.generateBindings(
                                className='__imported_%s' % (import_.replace('.','"),),
                                importNames = import_['names'][lineno],
                            )
                        )
            return str(thisModule)
        print createStandalone("myclass.py", importPath=["lib"])

    Known Bugs:

    *   Currently, imports that are not at the module level are not handed
        properly, and are replaced with no indentation.
    '''


    def __init__(self, moduleFileName, importPath=None):
        '''Create the StandaloneModule instance by loading the given module and
        processing it to locate the import statements.
        
        `moduleFileName` must be the full path to the module file.
        
        `importPath` may be provided as a list of directories in which to locate
        imports.  The directory that contains `moduleFileName` is implicitly added
        to `importPath`.  Any relative directories in `importPath` are relative to
        the directory that contains `moduleFileName`.
        '''
        self.moduleFileName = moduleFileName
        self.importPath = [os.path.dirname(moduleFileName)]
        if importPath:
            self.importPath = importPath + self.importPath
        self._analyze()

    def _analyze(self):
        # analyze the module by running it through the AST parser and finding the imports.
        module_ast = ast.parse(open(self.moduleFileName, 'rU').read(), self.moduleFileName, mode='exec')
        self.imports = {}
        new_ast = ImportNodeTransformer().visit(module_ast)
        print "".join(ASTFormatter().visit(new_ast))
        
    
    def __str__(self):
        '''Return a string of the module contents.'''
        return None # TODO: Not Yet Implemented
    
    def getImports(self):
        '''Return the list of imports for the module.

        Each import is represented as a dictionary with the following keys:

        *   `filename` holds the absolute pathname from which the module was loaded.

        *   `names` is a dictionary mapping (lineno,charno) to names.

            The (lineno,charno) pair locate where in the module file the import occurred.

            The mapped names can either be a single string or a list.

            If a single string, it is the name by which the imported module
            should be created in this module's namespace.

            If a list, it provides the `(imported_name,local_name)` pairs
            that will be mapped from the imported module's namespace into this
            module's namespace.
        '''
        return [] # TODO: Not Yet Implemented
    
    def getWarnings(self):
        '''Return the list of warnings for the module.
        
        Each warning reflects a line in the module file that contains both a "replaceable" import and a non-import or non-replaceable import - for example:
        
            import foo ; foo.doSomething()
        
        Warnings are repesented as dictionaries with the following keys:

        *   `fromFile` - the filename in which the import was located.  This is
            the same filename that the `StandaloneModule` instance was creaed
            with, but providing it in the warning makes error message formatting
            using the %(...) format easier.

        *   `importModule` - the full module name (including package, if
            present)

        *   `importLine` - the line number within `fromFile` where the import
            statement was found.
        '''
        return [] # TODO: Not Yet Implemented
    
    def replaceImport(self, import_, text):
        '''Replaces the named import in the module source with the given text.
        
        If multiple replaceable imports are locaed on the same line, this method
        will keep track of that so that the original `import` line gets deleted
        but the replaced imports are not affected.
        '''
        pass # TODO: Not Yet Implemented
    
    def wrapContents(self, className=None, importNames=None, indentLevel=4):
        '''Returns the module source, indented and wrapped with appropriate name
        bindings.
        
        If `className` is not provided, a class name will be chosen based on the
        module name.
        
        If `importNames` is not provided, then a single binding from the module
        name to the wrapped class name will be used.
        
        This method calls `self.generateBindings(className,importNames)` to
        implement the name bindings.
        '''
        return "" # TODO: Not Yet Implemented
    
    def generateBindings(self, className=None, importNames=None):
        '''Returns a string containing the local name bindings to the module's class.'''
        return "" # TODO: Not Yet Implemented
    
    def createStandalone(self):
        '''Creates a standalone version of the module.
        
        Using the other `StandaloneModule` methods, this method goes through each
        imported module, recursively generates a standalone version of that module,
        replaces its imports appropriately, and returns the new module text. 
        '''
        return "" # TODO: Not Yet Implemented
    
    def __repr__(self):
        return "%s(%s,importPath=%s)" % (self.__class__.__name__, repr(self.moduleFileName), repr(self.importPath))


if __name__ == '__main__':
    import inspect
    module = StandaloneModule(inspect.getfile(inspect.currentframe()))
    import pprint
    pprint.pprint(module)