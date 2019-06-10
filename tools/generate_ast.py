# Generate AST
import argparse
import os
import keyword
import builtins


def define_import(lines):
    lines.append("from loxtoken import LoxToken")
    lines.append("from typing import List")

# to define a visitor base class with visit method
# the specialized visitor will use decorators to build a mapping table of the method


def define_visitor_base_import(lines):
    lines.append("from visitorhelper import *")
    lines.append("from loxtoken import LoxToken")
    lines.append("from typing import List")


def define_visitormethods(visitor_lines, classname):
    # visitor method
    visitor_lines.append("\n")
    visitordef = "@visitor(" + classname + ")"
    visitor_lines.append(visitordef.rjust(len(visitordef)+4))
    if keyword.iskeyword(classname.lower() or classname.lower() in dir(builtins)):
        varname = "var_" + classname.lower()
    else:
        varname = classname.lower()
    visitordef = "def visit(self, " + varname + "):"
    visitor_lines.append(visitordef.rjust(len(visitordef)+4))

    visitordef = "return self.visit" + \
        classname.lower() + "(" + varname + ")"
    visitor_lines.append(visitordef.rjust(len(visitordef)+8))
    return visitor_lines


def define_visitor_file(visitor_lines, outputdir, basename):
    with open(define_filename(outputdir, basename), 'w') as f:
        # base class
        for l in visitor_lines:
            f.write(l+"\n")
    f.closed


def define_visitor_import(lines, basename):
    lines.insert(0, "from " + basename.lower() + " import *")

# to define a class with attributes valuated in init


def define_class(lines, classname, parentname, attributes):
    lines.append("\n")
    if len(parentname) > 0:
        classdef = "class " + classname + "(" + parentname + "):"
    else:
        classdef = "class " + classname + ":"
    lines.append(classdef)
    if (len(attributes) > 0):
        # split the string in (argname: type)
        initargs = [s[1]+": "+s[0]
                    for s in (x.split() for x in attributes.split(","))]
        initdef = "def __init__(self, " + ', '.join(initargs) + "):"
        lines.append(initdef.rjust(len(initdef)+4))
        for t in initargs:
            initval = "self." + t.split(":")[0] + " = " + t.split(":")[0]
            lines.append(initval.rjust(len(initval)+8))
    # visitor method
    visitordef = "def accept(self, visitor):"
    lines.append(visitordef.rjust(len(visitordef)+4))
    visitordef = "return visitor.visit(self)"
    lines.append(visitordef.rjust(len(visitordef)+8))
    return lines


def define_filename(outputdir, basename):
    filename = basename.lower()+".py"
    # no exhaustive check for the directory name neither write access.
    # you can consult https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
    if (not os.path.isabs(outputdir)):
        cwd = os.getcwd()
        directory = cwd + os.sep + outputdir
    else:
        directory = outputdir
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory + os.sep + filename

# Defining a set of classes from a main class


def define_ast(outputdir, basename, types, visitor_lines):
    lines = []
    newline = "\n"
    define_import(lines)
    define_visitor_import(visitor_lines, basename)
    if basename == "Stmt":
        lines.append("from expr import Expr, Variable")
    lines.append(newline)
    lines.append("class " + basename + ":")
    lines.append("pass".rjust(8))
    lines.append(newline)
    for type in types:
        typedef = type.split(":")
        typename = typedef[0].strip()
        define_class(lines, typename, basename, typedef[1])
    with open(define_filename(outputdir, basename), 'w') as f:
        # base class
        for l in lines:
            f.write(l+"\n")
    f.closed
    # Visitor
    for type in types:
        typedef = type.split(":")
        typename = typedef[0].strip()
        define_visitormethods(visitor_lines, typename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("generate_ast")
    parser.add_argument(
        "output_dir", help="output directory where the ast classes are generated", type=str)
    args = parser.parse_args()
    visitor_lines = []
    define_visitor_base_import(visitor_lines)
    visitor_lines.append("class Visitor:")
    # defining all the classes for the abstract syntax tree
    define_ast(args.output_dir, "Expr", [
        # Statements and State assign-Expression
        "Assign   : LoxToken name, Expr value",
        "Binary   : Expr left, LoxToken operator, Expr right",
        # Functions call-Expr
        "Call     : Expr callee, LoxToken paren, List[Expr] arguments",
        # Classes get-ast
        "Get      : Expr getobject, LoxToken name",
        "Grouping : Expr expression",
        "Literal  : object value",
        # Control Flow logical-ast
        "Logical  : Expr left, LoxToken operator, Expr right",
        # Classes set-ast
        "Set      : Expr setobject, LoxToken name, Expr value",
        # Inheritance super-Expr
        "Super    : LoxToken keyword, LoxToken method",
        # Classes this-ast
        "This     : LoxToken keyword",
        # Statements and State var-Expr
        "Unary    : LoxToken operator, Expr right",
        "Variable : LoxToken name"
    ], visitor_lines)

    # defining all the statements for the abstract syntax tree
    define_ast(args.output_dir, "Stmt", [
        # > block-ast
        "Block      : List[Stmt] statements",
        "Break      : LoxToken keyword",
        # Functions function-ast
        "Function   : LoxToken name, List[LoxToken] params, List[Stmt] body",
        #  Inheritance superclass-ast
        "Class      : LoxToken name, Variable superclass, List[Function] methods",
        #   Inheritance superclass-ast
        "Expression : Expr expression",
        # Control Flow if-ast
        "If         : Expr condition, Stmt thenbranch, Stmt elsebranch",
        # var-stmt-ast
        "Print      : Expr expression",
        # Functions return-ast
        "Return     : LoxToken keyword, Expr value",
        # Control Flow while-ast
        "Var        : LoxToken name, Expr initializer",
        "While      : Expr condition, Stmt body"
    ], visitor_lines)
    define_visitor_file(visitor_lines, args.output_dir, "Visitor")
