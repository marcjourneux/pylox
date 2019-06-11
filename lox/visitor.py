from lox.stmt import *
from lox.expr import *
from lox.visitorhelper import *
from lox.token import LoxToken
from typing import List


class Visitor:
    """Visitor class for Expr and Stmt, all visitors must inherit from this one."""

    @visitor(Assign)
    def visit(self, assign):
        return self.visitassign(assign)

    @visitor(Binary)
    def visit(self, binary):
        return self.visitbinary(binary)

    @visitor(Call)
    def visit(self, call):
        return self.visitcall(call)

    @visitor(FunctionExp)
    def visit(self, functionexp):
        return self.visitfunctionexp(functionexp)

    @visitor(Get)
    def visit(self, get):
        return self.visitget(get)

    @visitor(Grouping)
    def visit(self, grouping):
        return self.visitgrouping(grouping)

    @visitor(Literal)
    def visit(self, literal):
        return self.visitliteral(literal)

    @visitor(Logical)
    def visit(self, logical):
        return self.visitlogical(logical)

    @visitor(Set)
    def visit(self, set):
        return self.visitset(set)

    @visitor(Super)
    def visit(self, super):
        return self.visitsuper(super)

    @visitor(This)
    def visit(self, this):
        return self.visitthis(this)

    @visitor(Unary)
    def visit(self, unary):
        return self.visitunary(unary)

    @visitor(Variable)
    def visit(self, variable):
        return self.visitvariable(variable)

    @visitor(Block)
    def visit(self, block):
        return self.visitblock(block)

    @visitor(Break)
    def visit(self, var_break):
        return self.visitbreak(var_break)

    @visitor(Function)
    def visit(self, function):
        return self.visitfunction(function)

    @visitor(Class)
    def visit(self, var_class):
        return self.visitclass(var_class)

    @visitor(Expression)
    def visit(self, expression):
        return self.visitexpression(expression)

    @visitor(If)
    def visit(self, var_if):
        return self.visitif(var_if)

    @visitor(Print)
    def visit(self, print):
        return self.visitprint(print)

    @visitor(Return)
    def visit(self, var_return):
        return self.visitreturn(var_return)

    @visitor(Var)
    def visit(self, var):
        return self.visitvar(var)

    @visitor(While)
    def visit(self, var_while):
        return self.visitwhile(var_while)
