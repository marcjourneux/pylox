from lox.token import LoxToken
from typing import List
from lox.expr import Expr, Variable, FunctionExp


class Stmt:
    pass


class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit(self)


class Break(Stmt):
    def __init__(self, keyword: LoxToken):
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visit(self)


class Function(Stmt):
    def __init__(self, funcexp: FunctionExp):
        self.funcexp = funcexp

    def accept(self, visitor):
        return visitor.visit(self)


class Class(Stmt):
    def __init__(self, name: LoxToken, superclass: Variable, methods: List[Function]):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def accept(self, visitor):
        return visitor.visit(self)


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit(self)


class If(Stmt):
    def __init__(self, condition: Expr, thenbranch: Stmt, elsebranch: Stmt):
        self.condition = condition
        self.thenbranch = thenbranch
        self.elsebranch = elsebranch

    def accept(self, visitor):
        return visitor.visit(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit(self)


class Return(Stmt):
    def __init__(self, keyword: LoxToken, value: Expr):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visit(self)


class Var(Stmt):
    def __init__(self, name: LoxToken, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit(self)
