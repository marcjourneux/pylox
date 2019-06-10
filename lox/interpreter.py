# interpreter class for our lox language
# implemented with the visitor pattern
from lox.expr import *
from lox.stmt import *
from lox.environment import *
from lox.visitor import Visitor
from lox.token import LoxToken
from lox.tokentype import TokensDic as tk
from lox.callable import LoxCallable, LoxFunction, LoxClass
from lox.instance import LoxInstance
from lox.constants import LoxConstant
from lox.error import OperandsError, InterpreterError, DivisionByZeroError, ReturnException, BreakException
from lox.astprinter import PrinterVisitor
from lox.native import Clock
import operator

# Some python operator for all operations that do not require special process
op_dic = {
    tk.GREATER: operator.gt,
    tk.GREATER_EQUAL: operator.ge,
    tk.LESS: operator.lt,
    tk.LESS_EQUAL: operator.le,
    tk.MINUS: operator.sub,
    tk.STAR: operator.mul,
    tk.SLASH: operator.truediv,
    tk.BANG_EQUAL: operator.ne,
    tk.EQUAL_EQUAL: operator.eq
}


class Interpreter(Visitor):
    # Main environment
    global_env = Environment()
    locals = {}

    def __init__(self):
        self.current_env = self.global_env
        self.global_env.define("clock", Clock())

    def istruthy(self, value: object) -> bool:
        # I add 0 as a False value (nostalgia)
        if value is None:
            return False
        if value is False:
            return False
        if value is 0:
            return False
        if type(value) is bool:
            return value
        # everything else is true
        return True

    def check_number_operand(self, op: LoxToken, number: object, optype: str):
        if isinstance(number, (int, float, complex)):
            return
        raise OperandsError(op, optype, number)

    def check_number_operands(self, op: LoxToken, left: object, right: object, optype: tuple):
        if isinstance(left, optype) and isinstance(right, optype):
            return
        raise OperandsError(op, optype, left, right)

    def check_division_by_zero(self, op: LoxToken, left: object, right: object):
        if right == 0:
            raise DivisionByZeroError(op)
        return
    #
    # -------------------------
    # Expression visitor method
    # -------------------------
    #

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

    def visitassign(self, expr: Assign) -> object:
        var_value = self.evaluate(expr.value)
        distance = 0
        if expr in self.locals:
            distance = self.locals[expr]
        if distance:
            self.current_env.assignat(distance, expr.name, var_value)
        else:
            self.global_env.assign(expr.name, var_value)
        return var_value

    def visitcall(self, expr: Call) -> object:
        callee = self.evaluate(expr.callee)
        resolved_args = []
        for arg in expr.arguments:
            resolved_args.append(self.evaluate(arg))
        if not isinstance(callee, LoxCallable):
            raise InterpreterError(expr.paren, "can only call functions.")
        if len(resolved_args) is not callee.arity():
            raise InterpreterError(expr.paren, "expected " +
                                   callee.arity() + " arguments. " + len(resolved_args) + " were provided.")
        try:
            return callee.call(self, resolved_args)
        except ReturnException as exc:
            return exc.value
        finally:
            pass

    def visitfunctionexp(self, expr: FunctionExp) -> object:
        # Create a callable function from the declaration
        return LoxFunction(None, expr, self.current_env)

    def visitget(self, expr: Get) -> object:
        getobj = self.evaluate(expr.getobject)
        if isinstance(getobj, LoxInstance):
            return getobj.get_property(expr.name)
        raise InterpreterError(
            expr.name, "Properties are allowed on instances only.")

    def visitset(self, expr: Set) -> object:
        setobj = self.evaluate(expr.setobject)
        if not isinstance(setobj, LoxInstance):
            raise InterpreterError(
                expr.name, "Properties can only be set on instances.")
        value = self.evaluate(expr.value)
        setobj.set_property(expr.name, value)

    def visitliteral(self, expr: Literal) -> object:
        return expr.value

    def visitlogical(self, expr: Logical) -> object:
        left = self.evaluate(expr.left)
        if expr.operator.type == tk.OR:
            if self.istruthy(left):
                return left
        else:
            if not self.istruthy(left):
                return left
        return self.evaluate(expr.right)

    def visitgrouping(self, expr: Grouping) -> object:
        return self.evaluate(expr.expr)

    def visitunary(self, expr: Unary) -> object:
        right = self.evaluate(expr.right)
        if expr.operator.type == tk.MINUS:
            self.check_number_operand(expr.operator, expr.operator.type, right)
            return -right
        elif expr.operator.type == tk.BANG:
            return not right

    def visitbinary(self, expr: Binary) -> object:
        right = self.evaluate(expr.right)
        left = self.evaluate(expr.left)
        op_type = expr.operator.type
        # Arithmetic operations
        if op_type == tk.MINUS:
            self.check_number_operands(
                expr.operator, left, right, (int, float, complex))
            return left - right
        elif op_type == tk.STAR:
            self.check_number_operands(
                expr.operator, left, right, (int, float, complex))
            return left * right
        elif op_type == tk.SLASH:
            self.check_number_operands(
                expr.operator, left, right, (int, float, complex))
            self.check_division_by_zero(expr.operator, left, right)
            return left / right
        elif op_type == tk.PLUS:
            # Just for learning purpose as Python would handle that
            if type(left) is str and type(right) is str:
                return left + right
            # Notice that the below test will work if right or left is True
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            # Mixed type
            elif type(left) is str and isinstance(right, (int, float)):
                return left + str(right)
            elif type(right) is str and isinstance(left, (int, float)):
                return str(left) + right
        # Comparison operators: python operator are matching lox requirements
        # Notice that we follow IEEE 754 with operator equal, as NaN != NaN in python
        # We diverge here a bit from the Java isequal
        elif op_type in (tk.GREATER, tk.GREATER_EQUAL, tk.LESS, tk.LESS_EQUAL, tk.BANG_EQUAL, tk.EQUAL_EQUAL):
            self.check_number_operands(
                expr.operator, left, right, (int, float, complex, str))
            operator_function = op_dic[op_type]
            return operator_function(left, right)
        # No matches
        return None

    def lookupvariable(self, name, expr):
        if expr in self.locals:
            return self.current_env.getat(self.locals[expr], name)
        else:
            return self.global_env.get(name)

    def visitvariable(self, expr: Variable) -> object:
        return self.lookupvariable(expr.name, expr)
        # return self.current_env.get(expr.name) -- removed for resolver

    def visitthis(self, expr: This) -> object:
        return self.lookupvariable(expr.keyword, expr)

    def visitsuper(self, expr: Super) -> object:
        """Retrieve the super class method and bind the method to the instance"""
        distance = self.locals.get(expr, 0)
        superclass = self.current_env.getat(
            distance, tk.lexeme_from_type[tk.SUPER])
        # 'this' is always just below super env
        inst = self.current_env.getat(distance-1, tk.lexeme_from_type[tk.THIS])
        method = superclass.findmethod(expr.method)
        if method is not None:
            return method.bind(inst)
        else:
            raise InterpreterError(
                expr.name, "Properties can only be set on instances.")

    #
    # -------------------------
    # Statement visitor method
    # -------------------------
    #

    def visitblock(self, blockstmt: Block):
        self.executeblock(blockstmt.statements, Environment(self.current_env))

    def visitbreak(self, breakstmt: Break):
        raise BreakException(breakstmt.keyword)

    def visitclass(self, classstmt: Class):
        superclass = None
        if classstmt.superclass is not None:
            superclass = self.evaluate(classstmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise InterpreterError(
                    classstmt.name, "Superclass must be a class.")
        self.current_env.define(classstmt.name.lexeme, None)
        if superclass:
            self.current_env = Environment(self.current_env)
            self.current_env.define(tk.lexeme_from_type[tk.SUPER], superclass)
        methods = []
        for method in classstmt.methods:
            # fixme
            methods.append(LoxFunction(
                method.name, method, self.current_env))
        lxclass = LoxClass(classstmt.name.lexeme, superclass, methods)
        if superclass:
            self.current_env = self.current_env.enclosing
        self.current_env.assign(classstmt.name, lxclass)

    def visitexpression(self, expstmt: Expression):
        self.evaluate(expstmt.expression)

    def visitfunction(self, function: Function):
        # Create a callable function from the declaration
        callable = LoxFunction(
            function.funcexp.name, function.funcexp, self.current_env)
        # Put the callable in the environment: how simple, it seems !
        self.current_env.define(function.funcexp.name.lexeme, callable)

    def visitif(self, ifstmt: Stmt):
        if self.istruthy(self.evaluate(ifstmt.condition)):
            self.execute(ifstmt.thenbranch)
        else:
            if ifstmt.elsebranch is not None:
                self.execute(ifstmt.elsebranch)

    def visitprint(self, printstmt: Print):
        print(str(self.evaluate(printstmt.expression)))

    def visitreturn(self, returnstmt: Return):
        returnvalue = None
        if returnstmt.value is not None:
            returnvalue = self.evaluate(returnstmt.value)
        raise ReturnException(returnvalue)

    def visitvar(self, varstmt: Var):
        value = None
        if varstmt.initializer is not None:
            value = self.evaluate(varstmt.initializer)
        self.current_env.define(varstmt.name.lexeme, value)

    def visitwhile(self, whilestmt: While):
        try:
            while self.istruthy(self.evaluate(whilestmt.condition)):
                self.execute(whilestmt.body)
        except BreakException as exc:
            pass

    def execute(self, statement: Stmt):
        statement.accept(self)

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def executeblock(self, liststmt: List[Stmt], environment: Environment):
        # Create a new env for this block
        previous_env = self.current_env
        self.current_env = environment
        # Execute all the statements of the block in the new env
        try:
            for statement in liststmt:
                self.execute(statement)
        finally:
            self.current_env = previous_env

    def interpret(self, statements: List[Stmt]) -> object:
        try:
            astprinter = PrinterVisitor()
            for statement in statements:
                if statement is not None:
                    print(astprinter.print(statement))
                    self.execute(statement)
                else:
                    print("None stamement, error detected.")
        except InterpreterError as error:
            print("error: ", error)
