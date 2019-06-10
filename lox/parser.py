# Parser class that will consume a list of token to build the grammar
from lox.token import LoxToken
from lox.tokentype import TokensDic as Tk
from lox.constants import LoxConstant
from lox.stmt import *
from lox.expr import *
from lox.visitor import Visitor
from lox.error import ParserError, LoxError
from lox.functiontypes import FunctionType

from typing import List


class Parser:
    #
    # The parser is initialized with the list of tokens to parse
    def __init__(self, tokens: LoxToken):
        self.tokens = tokens
        self.current = 0

    #
    # get the current token without moving forward
    def peek(self) -> LoxToken:
        return self.tokens[self.current]

    #
    # Get previous token
    def previous(self) -> LoxToken:
        if self.current > 0:
            return self.tokens[self.current-1]
        else:
            return None

    #
    # Get next token
    def next(self) -> LoxToken:
        if self.is_at_end():
            raise ParserError(
                self.peek(), "reached end of file, cannot get next token.")
        return self.tokens[self.current+1]

    #
    # Check we did not reach the end of the file
    def is_at_end(self) -> bool:
        return self.peek().type == Tk.EOF

    #
    # Check the token type whithout moving forward
    def check(self, ttype: str) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == ttype

    #
    # Check the next token type whithout moving forward
    def checknext(self, ttype: str) -> bool:
        if self.is_at_end():
            return False
        return self.next().type == ttype

    #
    # To check if the current token type is any of the input list.
    # If so consume the token (advance) that can be retrieved with previous()
    def match(self, *tokentypes: List[str]) -> bool:
        for t in tokentypes:
            if self.check(t):
                self.advance()
                return True
        return False

    #
    # Consume and return token
    def advance(self) -> LoxToken:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    #
    # Check if the next token is of the specified type and return it, otherwise return an error
    # moves forward if so.
    def consume(self, ttype: str, message: str) -> LoxToken:
        # print("--> in parserconsume: Token:",
        #     self.tokens[self.current].type, " to compare with: ", ttype)
        if self.check(ttype):
            return self.advance()
        raise ParserError(self.peek(), message)

    #
    # -------------------------------------------------
    # Statement functions
    # -------------------------------------------------
    #
    def declaration(self) -> Stmt:
        try:
            # variable declaration statement
            if self.match(Tk.VAR):
                return self.vardeclaration()
            # function declaration statement
            elif self.check(Tk.FUN):  # and self.checknext(Tk.IDENTIFIER):
                return self.fundeclaration()
            # class declaration statement
            elif self.match(Tk.CLASS):
                return self.classdeclaration()
            # generic statement
            else:
                return self.statement()

        except ParserError as err:
            print("error in parsing at token " +
                  str(self.previous()) + " " + err.message)
            return None
            # self.synchronize()

    def vardeclaration(self) -> Stmt:
        # Let's get the identifier
        tk_varname = self.consume(
            Tk.IDENTIFIER, "Expect a variable identifier")
        # Retrieve the initializing expression
        initializer = None
        if self.match(Tk.EQUAL):
            initializer = self.expression()
        # Make sure the statement has a termination statement
        self.consume(Tk.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(tk_varname, initializer)

    def fundeclaration(self) -> Stmt:
        self.consume(Tk.FUN, "Expect 'fun' for function statement.")
        # a function statement should not be anonymous and is not a lambda
        return Function(self.functionbody(FunctionType.FUNCTION))

    def classdeclaration(self) -> Stmt:
        superclass = None
        name = self.consume(
            Tk.IDENTIFIER, "Expect a class name after 'class'.")
        if self.match(Tk.LESS):
            self.consume(
                Tk.IDENTIFIER, "Expect a super class name after '<'.")
            superclass = Variable(self.previous())
        self.consume(Tk.LEFT_BRACE, "Expect a '{' name after class name.")
        methods = []
        while not self.check(Tk.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.functionbody(FunctionType.METHOD))
        self.consume(Tk.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, superclass, methods)

    def statement(self) -> Stmt:
        if self.match(Tk.PRINT):
            return self.printstatement()
        if self.match(Tk.LEFT_BRACE):
            return Block(self.blockstatement())
        if self.match(Tk.IF):
            return self.ifstatement()
        if self.match(Tk.WHILE):
            return self.whilestatement()
        if self.match(Tk.FOR):
            return self.forstatement()
        if self.match(Tk.BREAK):
            return self.breakstatement()
        if self.match(Tk.RETURN):
            return self.returnstatement()
        return self.expressionstatement()

    def ifstatement(self) -> Stmt:
        self.consume(Tk.LEFT_PAREN,
                     "expect a ( at the start of the if condition.")
        condition = self.expression()
        self.consume(Tk.RIGHT_PAREN,
                     "expect a ) at the end of the if condition.")
        thenbranch = self.statement()
        elsebranch = None
        if self.match(Tk.ELSE):
            elsebranch = self.statement
        return If(condition, thenbranch, elsebranch)

    def whilestatement(self) -> Stmt:
        self.consume(Tk.LEFT_PAREN,
                     "expect a ( at the start of the 'while' condition.")
        condition = self.expression()
        self.consume(Tk.RIGHT_PAREN,
                     "expect a ) at the end of the 'while' condition.")
        body = self.statement()
        return While(condition, body)

    def forstatement(self) -> Stmt:
        self.consume(Tk.LEFT_PAREN, "expect a ( after a 'for'.")
        initializer = None
        if self.match(Tk.VAR):
            initializer = self.vardeclaration()
        elif not self.match(Tk.SEMICOLON):
            initializer = self.expressionstatement()
        condition = None
        if not self.check(Tk.SEMICOLON):
            condition = self.expression()
            self.consume(Tk.SEMICOLON, "expect a ; after 'for' condition.")
        increment = None
        if not self.check(Tk.RIGHT_PAREN):
            increment = self.expression()
            self.consume(Tk.RIGHT_PAREN,
                         "expect a ) at the end of the 'for' increment.")
        body = self.statement()
        # Build the equivalent while loop
        # --> first create a while loop with condition + (body, increment)
        body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        # --> add the initializer
        if initializer is not None:
            body = Block([initializer, body])
        return body

    def blockstatement(self) -> List[Stmt]:
        statements = []
        while not self.is_at_end() and not self.check(Tk.RIGHT_BRACE):
            statements.append(self.declaration())
        self.consume(Tk.RIGHT_BRACE, "expect } at the end of block.")
        return statements

    def breakstatement(self) -> Stmt:
        self.consume(Tk.SEMICOLON, "expect a ';' after a 'break'.")
        return Break(self.previous())

    # def varstatement(self) -> Stmt:
    #     try:
    #         if self.match(Tk.VAR):
    #             return self.vardeclaration()
    #         return self.statement()
    #     except ParserError as err:
    #         pass
    #         # self.synchronize(err)

    def printstatement(self) -> Stmt:
        value = self.expression()
        # consume the semicolon that should be at the end of the statement
        self.consume(Tk.SEMICOLON, "expecting a ';' at the end of the line.")
        return Print(value)

    def returnstatement(self) -> Stmt:
        keyword = self.previous()
        value = None
        if not self.check(Tk.SEMICOLON):
            value = self.expression()
        self.consume(
            Tk.SEMICOLON, "expect a ';' at the end of the 'return' statement.")
        return Return(keyword, value)

    def expressionstatement(self) -> Stmt:
        # Retrieve the expression in the statement
        expr = self.expression()
        # Consume the ; token
        self.consume(Tk.SEMICOLON, "expecting a ; at the end of the line")
        return Expression(expr)
    #
    # --------------------------------------
    # Expressions functions
    # --------------------------------------
    #

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        # Consider the possible left hand side of the assignment as any expression
        expr = self.logic_or()
        # if we match the = we know it is a candidate for assignment
        if self.match(Tk.EQUAL):
            tk_equals = self.previous()
            # assignment are right associative, so we neeed to parse them right recursively
            right = self.assignment()
            # if the l-value is a possible variable, return the assignment
            if isinstance(expr, Variable):
                return Assign(expr.name, right)
            # we can also assign instances property
            elif isinstance(expr, Get):
                return Set(expr.getobject, expr.name, right)
            # we do not have a variable like, error
            raise ParserError(tk_equals, "invalid assignment target")
        # the expression is not an assignment
        return expr

    def logic_or(self) -> Expr:
        expr = self.logic_and()
        while (self.match(Tk.OR)):
            logic_op = self.previous()
            right = self.logic_and()
            expr = Logical(expr, logic_op, right)
        return expr

    def logic_and(self) -> Expr:
        expr = self.equality()
        while (self.match(Tk.AND)):
            logic_op = self.previous()
            right = self.equality()
            expr = Logical(expr, logic_op, right)
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(Tk.EQUAL_EQUAL, Tk.BANG_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.addition()

        while self.match(Tk.GREATER_EQUAL, Tk.GREATER,
                         Tk.LESS, Tk.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expr = Binary(expr, operator, right)
        return expr

    def addition(self) -> Expr:
        expr = self.multiplication()

        while self.match(Tk.PLUS, Tk.MINUS):
            operator = self.previous()
            right = self.multiplication()
            expr = Binary(expr, operator, right)
        return expr

    def multiplication(self) -> Expr:
        expr = self.unary()

        while self.match(Tk.SLASH, Tk.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        # this time we have a right associative operator
        while self.match(Tk.MINUS, Tk.BANG):
            operator = self.previous()
            right = self.unary()
            # we loop until all operators are consumed
            return Unary(operator, right)
        # no more operator, we have a call expr
        return self.call()

    def call(self) -> Expr:
        expr = self.primary()
        # Let's parse function call (passing the callee) as long as we have paranthesis
        while True:
            if self.match(Tk.LEFT_PAREN):
                expr = self.finishcall(expr)
            elif self.match(Tk.DOT):
                name = self.consume(
                    Tk.IDENTIFIER, "Expect a property name after the '.'")
                expr = Get(expr, name)
            else:
                break
        return expr

    def finishcall(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check(Tk.RIGHT_PAREN):
            while "let's parse arguments as long as we have commas":
                arguments.append(self.expression())
                if not self.match(Tk.COMMA):
                    break
        if len(arguments) > LoxConstant.max_param:
            LoxError.error(self.peek(),
                           "function cannot have more than 8 arguments")
        call_left_paren = self.consume(
            Tk.RIGHT_PAREN, "expect a ')' at the end of a function call.")
        return Call(callee, call_left_paren, arguments)

    def functionbody(self, kind: FunctionType):
        funcid = None
        functiontype = kind
        if kind is FunctionType.FUNCTION:
            funcid = self.consume(
                Tk.IDENTIFIER, "Expect a function name after 'fun'.")
            self.consume(Tk.LEFT_PAREN, "expect a '(' after function name.")
        elif kind is FunctionType.LAMBDA:
            self.consume(Tk.LEFT_PAREN, "expect a '(' after 'fun' for lambda.")
        elif kind is FunctionType.METHOD:
            funcid = self.consume(Tk.IDENTIFIER, "Expect a method name.")
            if funcid is LoxConstant.init_method:
                functiontype = FunctionType.INIT
            self.consume(Tk.LEFT_PAREN, "expect a '(' after method name.")
        else:
            raise ParserError(
                self.previous(), "Unexpected function type in parser.")
        parameters = []
        # All parameters should be identifiers
        if not self.check(Tk.RIGHT_PAREN):
            while "we have comma after the parameter":
                parameters.append(
                    self.consume(Tk.IDENTIFIER, "expect identifiers as function parameters."))
                if len(parameters) > LoxConstant.max_param:
                    LoxError.error(self.previous(
                    ), "function can take at most " + LoxConstant.max_param + " parameters.")
                if not self.match(Tk.COMMA):
                    break
        self.consume(Tk.RIGHT_PAREN,
                     "expect a ) at the end of the function parameters.")
        # Parse the body of the function
        self.consume(
            Tk.LEFT_BRACE, "expect a { after function parameters list.")
        body = self.blockstatement()
        return FunctionExp(funcid, parameters, body, functiontype)

    def primary(self) -> Expr:
        if self.match(Tk.FALSE):
            return Literal(False)

        if self.match(Tk.TRUE):
            return Literal(True)

        if self.match(Tk.NIL):
            return Literal(None)

        if self.match(Tk.NUMBER, Tk.STRING):
            return Literal(self.previous().literal)

        if self.match(Tk.IDENTIFIER):
            return Variable(self.previous())

        # I consider function definition in expression as lambda. Open to discussion
        if self.match(Tk.FUN):
            return self.functionbody(FunctionType.LAMBDA)

        if self.match(Tk.THIS):
            return This(self.previous())

        if self.match(Tk.SUPER):
            keyword = self.previous()
            self.consume(Tk.DOT, "Expect a '.' after 'super'.")
            method = self.consume(
                Tk.IDENTIFIER, "Expect superclass method name after 'super.'.")
            return Super(keyword, method)

        if self.match(Tk.LEFT_PAREN):
            expr = self.expression()
            self.consume(Tk.RIGHT_PAREN, "Expect ')' after expr.")
            return Grouping(expr)

        raise ParserError(self.peek(), "expecting an expr.")
    #
    # Parsing the list of statements

    def parse(self) -> List[Stmt]:
        try:
            statements = []
            while not self.is_at_end():
                statements.append(self.declaration())

            return statements
        except ParserError as e:
            print(e.message)
