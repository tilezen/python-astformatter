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

from ASTFormatter import ASTFormatter

########################################################################
# 3rd party libraries
# (if any)

# import codegen

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
    def visit_Import(self, node):
        replacementNodes = [
            self._processNode(
                alias.name,
                module_as=alias.asname,
                lineno=node.lineno,
                charno=node.col_offset
            ) for alias in node.names
        ]
        return replacementNodes
    def visit_ImportFrom(self, node):
        replacementNodes = [
            self._processNode(
                node.module,
                import_names=[(alias.name, alias.asname) for alias in node.names],
                relative_level=node.level,
                lineno=node.lineno,
                charno=node.col_offset
            )
        ]
        return replacementNodes

    def _processNode(
            self, module, module_as=None,
            import_names=None, relative_level=None,
            lineno=None, charno=None):
#       print "importing module %s(%s) names %s level %s location %s:%s" % (repr(module), repr(module_as), repr(import_names), repr(relative_level), repr(lineno), repr(charno))
        if import_names is None:
#           if module_as is None:
#               module_as = module
            return ast.Import(ast.alias(module, module_as), lineno=lineno, col_offset=charno)
        else:
            return ast.ImportFrom(module, [ast.alias(name, asname) for (name, asname) in import_names], relative_level, lineno=lineno, col_offset=charno)

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
        return None  # TODO: Not Yet Implemented
    
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
        return []  # TODO: Not Yet Implemented
    
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
        return []  # TODO: Not Yet Implemented
    
    def replaceImport(self, import_, text):
        '''Replaces the named import in the module source with the given text.
        
        If multiple replaceable imports are locaed on the same line, this method
        will keep track of that so that the original `import` line gets deleted
        but the replaced imports are not affected.
        '''
        pass  # TODO: Not Yet Implemented
    
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
        return ""  # TODO: Not Yet Implemented
    
    def generateBindings(self, className=None, importNames=None):
        '''Returns a string containing the local name bindings to the module's class.'''
        return ""  # TODO: Not Yet Implemented
    
    def createStandalone(self):
        '''Creates a standalone version of the module.
        
        Using the other `StandaloneModule` methods, this method goes through each
        imported module, recursively generates a standalone version of that module,
        replaces its imports appropriately, and returns the new module text. 
        '''
        return ""  # TODO: Not Yet Implemented
    
    def __repr__(self):
        return "%s(%s,importPath=%s)" % (self.__class__.__name__, repr(self.moduleFileName), repr(self.importPath))


if __name__ == '__main__':
    import inspect
    if len(sys.argv) > 1:
        module = StandaloneModule(sys.argv[1])
    else:
        module = StandaloneModule(inspect.getfile(inspect.currentframe()))
    import pprint
    # pprint.pprint(module)
