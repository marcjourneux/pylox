from lox.visitor import Visitor
from lox.interpreter import Interpreter
from lox.stmt import Stmt
from lox.token import LoxToken
from lox.tokentype import TokensDic as Tk
from lox.error import LoxError
from lox.astprinter import PrinterVisitor
from lox.functiontypes import FunctionType
from lox.classtypes import ClassType
from typing import List


class Resolver(Visitor):
    """Class to manage scopes and variable resolution."""

    def __init__(self, interpreter):
        """Resolver attributes:

        scopes -- is a list of scopes managed as a stack
        interpreter -- the lox interpreter"""
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def beginscope(self):
        self.scopes.append({})

    def endscope(self):
        self.scopes.pop()

    def resolvelist(self, statements: List[Stmt]):
        for stmt in statements:
            self.resolve(stmt)

    def resolve(self, obj):
        obj.accept(self)

    def resolvelocal(self, expr, name: LoxToken):
        """Look for the closest scope of a variable by its name."""
        i = 0
        for scope in reversed(self.scopes):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return
            i += 1

    # def resolvefunction(self, function, functiontype):
    #     enclosing_function = self.current_function
    #     self.current_function = functiontype
    #     self.resolve(function)
    #     self.current_function = enclosing_function

    def declare(self, name: LoxToken):
        """Declare a variable in the current scope and mark it non initialized."""
        if not self.scopes:
            return
        # we retrieve the in-work scope
        scope = self.scopes[-1]
        # If the variable is already there, send an error
        if name.lexeme in scope:
            LoxError.error(
                name, "A variable with this name has already been declared in the same scope.")
            return
        # variable is marked False as it is not initialized yet
        scope[name.lexeme] = False

    def define(self, name: LoxToken):
        """Mark a variable in the current / innermost scope as being initialized"""
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def visitassign(self, assign):
        self.resolve(assign.value)
        self.resolvelocal(assign, assign.name)

    def visitbinary(self, binary):
        self.resolve(binary.left)
        self.resolve(binary.right)

    def visitcall(self, call):
        self.resolve(call.callee)
        for arg in call.arguments:
            self.resolve(arg)

    def visitfunctionexp(self, functionexp):
        enclosing_function = self.current_function
        self.current_function = functionexp.functiontype
        self.beginscope()
        for param in functionexp.params:
            self.declare(param)
            self.define(param)
        self.resolvelist(functionexp.body)
        self.endscope()
        self.current_function = enclosing_function

    def visitget(self, get):
        self.resolve(get.getobject)

    def visitgrouping(self, grouping):
        self.resolve(grouping.expression)

    def visitliteral(self, literal):
        pass

    def visitlogical(self, logical):
        self.resolve(logical.left)
        self.resolve(logical.right)

    def visitset(self, var_set):
        self.resolve(var_set.value)
        self.resolve(var_set.setobject)

    def visitsuper(self, var_super):
        if self.current_class is ClassType.NONE:
            LoxError.error(
                var_super.keyword, "Cannot use 'super' outside of a class.")
        if self.current_class is ClassType.CLASS:
            LoxError.error(
                var_super.keyword, "Cannot use 'super' in a class with no superclass.")
        self.resolvelocal(var_super, var_super.keyword)

    def visitthis(self, this):
        if self.current_class is ClassType.NONE:
            LoxError.error(
                this.keyword, "Cannot use 'this' outside of a class.")
        self.resolvelocal(this, this.keyword)

    def visitunary(self, unary):
        self.resolve(unary.right)

    def visitvariable(self, variable):
        """Resolve Variable expression.

        Do not allow the variable to initialize with itself."""
        if self.scopes and variable.name.lexeme in self.scopes[-1]:
            if self.scopes[-1][variable.name.lexeme] == False:
                LoxError.error(
                    variable.name, "Cannot use local variable in its own initializer.")
        self.resolvelocal(variable, variable.name)

    def visitblock(self, block):
        self.beginscope()
        self.resolvelist(block.statements)
        self.endscope()

    def visitbreak(self, var_break):
        pass

    def visitfunction(self, function):
        self.declare(function.funcexp.name)
        self.define(function.funcexp.name)
        self.resolve(function.funcexp)

    def visitclass(self, var_class):
        self.declare(var_class.name)
        self.define(var_class.name)
        if var_class.superclass is not None:
            if var_class.superclass.name.lexeme is var_class.name.lexeme:
                LoxError.error(var_class.name,
                               "Class cannot have the same name as super class.")
            self.resolve(var_class.superclass)
        previous_class = self.current_class
        self.current_class = ClassType.CLASS
        # add the scope for the super keyword
        if var_class.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.beginscope()
            self.scopes[-1][Tk.lexeme_from_type[Tk.SUPER]] = True
        # Define the 'this'
        self.beginscope()
        self.scopes[-1][Tk.lexeme_from_type[Tk.THIS]] = True
        for method in var_class.methods:
            self.resolve(method)
        self.endscope()
        if var_class.superclass is not None:
            self.endscope()
        self.current_class = previous_class

    def visitexpression(self, expression):
        self.resolve(expression.expression)

    def visitif(self, var_if):
        self.resolve(var_if.condition)
        self.resolve(var_if.thenbranch)
        if var_if.elsebranch is not None:
            self.resolve(var_if.elsebranch)

    def visitprint(self, print):
        self.resolve(print.expression)

    def visitreturn(self, var_return):
        if self.current_function == FunctionType.NONE:
            LoxError.error(var_return.keyword,
                           "Cannot return from top-level code.")
        if var_return.value is not None:
            if self.current_function is FunctionType.INIT:
                LoxError.error(var_return.keyword,
                               "Cannot return value from an initializer.")
            self.resolve(var_return.value)

    def visitvar(self, var):
        """Resolving variable declaration. """
        self.declare(var.name)
        if var.initializer is not None:
            self.resolve(var.initializer)
        self.define(var.name)

    def visitwhile(self, var_while):
        self.resolve(var_while.condition)
        self.resolve(var_while.body)
