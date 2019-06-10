from lox.token import LoxToken
from typing import List


class Expr:
    pass


class Assign(Expr):
    def __init__(self, name: LoxToken, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit(self)


class Binary(Expr):
    def __init__(self, left: Expr, operator: LoxToken, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit(self)


class Call(Expr):
    def __init__(self, callee: Expr, paren: LoxToken, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit(self)


class FunctionExp(Expr):
    def __init__(self, name: LoxToken, params: List[LoxToken], body: "List[Stmt]", functiontype):
        self.name = name
        self.params = params
        self.body = body
        self.functiontype = functiontype

    def accept(self, visitor):
        return visitor.visit(self)


class Get(Expr):
    def __init__(self, getobject: Expr, name: LoxToken):
        self.getobject = getobject
        self.name = name

    def accept(self, visitor):
        return visitor.visit(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit(self)


class Literal(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor):
        return visitor.visit(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: LoxToken, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit(self)


class Set(Expr):
    def __init__(self, setobject: Expr, name: LoxToken, value: Expr):
        self.setobject = setobject
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit(self)


class Super(Expr):
    def __init__(self, keyword: LoxToken, method: LoxToken):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor):
        return visitor.visit(self)


class This(Expr):
    def __init__(self, keyword: LoxToken):
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visit(self)


class Unary(Expr):
    def __init__(self, operator: LoxToken, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit(self)


class Variable(Expr):
    def __init__(self, name: LoxToken):
        self.name = name

    def accept(self, visitor):
        return visitor.visit(self)
