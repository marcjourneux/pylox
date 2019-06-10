# This is the start of a __str__ implementation for expr
from lox.expr import *
from lox.stmt import Stmt
from typing import List
from lox.visitor import Visitor


class PrinterVisitor(Visitor):
    def print(self, item):
        return item.accept(self)

    def parenthesize(self, name: str, exprs: List[Expr]):
        result = "(" + name
        for e in exprs:
            if isinstance(e, (Expr, Stmt)):
                result += " " + e.accept(self)
            else:
                result += " " + str(e)
        result += ")"
        return result

    def visitassign(self, assign):
        return "Assigning: " + self.parenthesize(assign.name.lexeme, ["<-", assign.value])

    def visitcall(self, call_def):
        call_str = "<calling fn: " + call_def.callee.accept(self) + "> "
        call_str += self.parenthesize("with args:", call_def.arguments)
        return call_str

    def visitbinary(self, binary):
        return self.parenthesize(binary.operator.lexeme, [binary.left, binary.right])

    def visitfunctionexp(self, functionexp):
        return self.parenthesize("fn", functionexp.params)

    def visitget(self, get):
        return self.parenthesize("get", [get.name])

    def visitgrouping(self, grouping):
        return self.parenthesize("group", [grouping.expr])

    def visitliteral(self, literal):
        if not literal.value:
            return "nil"
        else:
            return str(literal.value)

    def visitlogical(self, logical):
        return self.parenthesize("Logical" + logical.operator.lexeme, [logical.left, logical.right])

    def visitset(self, var_set):
        return self.parenthesize("set", [var_set.name])

    def visitvariable(self, variable):
        return "variable:" + str(variable.name)

    def visitunary(self, unary):
        return self.parenthesize(unary.operator.lexeme, [unary.right])

    # -------------------------------------------
    # Statements
    # -------------------------------------------
    #

    def visitblock(self, blockstmt):
        return self.parenthesize("Block with first statement:", [blockstmt.statements[0]])

    def visitbreak(self, breakstmt):
        return "(Break)"

    def visitfunction(self, funcstmt):
        return self.parenthesize("Function", [funcstmt.funcexp.name.lexeme])

    def visitclass(self, classstmt):
        return self.parenthesize("Class", [classstmt.name])

    def visitexpression(self, expstmt):
        return self.parenthesize("Expression statement", [expstmt.expression])

    def visitif(self, ifstmt):
        return self.parenthesize("If", [ifstmt.condition, ifstmt.thenbranch, ifstmt.elsebranch])

    def visitprint(self, printstmt):
        return self.parenthesize("Print", [printstmt.expression])

    def visitreturn(self, returnstmt):
        return self.parenthesize("Return", [returnstmt.value])

    def visitvar(self, varstmt):
        return self.parenthesize("Var", [varstmt.name, varstmt.initializer])

    def visitwhile(self, whilestmt):
        return self.parenthesize("While", [whilestmt.condition])


if __name__ == "__main__":
    expr = Binary(
        Unary(
            LoxToken("MINUS", "-", "", 1),
            Literal(123)),
        LoxToken("STAR", "*", "", 1),
        Grouping(Literal(45.67)))

    printer = PrinterVisitor()
    print(printer.print(expr))
