from lox.token import LoxToken
from lox.tokentype import TokensDic


class LoxRuntimeError(Exception):
    def __init__(self, token: LoxToken, errordescription: str):
        self.token = token

        super().__init__(errordescription)


class ParserError(Exception):
    def __init__(self, token: LoxToken, errordescription: str):
        self.token = token
        if token.type == TokensDic.EOF:
            self.message = str(token.line) + " at end " + errordescription
        else:
            self.message = str(token.line) + " at '" + \
                token.lexeme + "' " + errordescription
        super().__init__(self.message)


class InterpreterError(Exception):
    def __init__(self, token: LoxToken, errordescription: str):
        self.token = token
        super().__init__(errordescription)


class OperandsError(InterpreterError):
    def __init__(self, token: LoxToken, typedescription: str = "", left: object = None, right: object = None):
        if left is not None and right is None:
            self.message = str(token.lexeme) + " operator requires " + typedescription + ". " +  \
                str(left) + " is not " + typedescription
        elif left is not None and right is not None:
            self.message = str(token.lexeme) + " operator requires " + typedescription + ". " +  \
                str(left) + " and " + str(right) + \
                " are not " + typedescription
        super().__init__(token, self.message)


class DivisionByZeroError(InterpreterError):
    def __init__(self, token: LoxToken):
        self.message = "Division by zero line:" + token.line
        super().__init__(token, self.message)


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    def __init__(self, value):
        self.value = value


class LoxError:
    log = []
    haderror = False

    @staticmethod
    def report(line, where, message):
        logmsg = "[line {}] Error {}: {}".format(line, where, message)
        LoxError.log.append(logmsg)
        print(logmsg)

    @staticmethod
    def error(lineinfo, message):
        if isinstance(lineinfo, LoxToken):
            linenumber = lineinfo.line
        else:
            linenumber = lineinfo
        LoxError.haderror = True
        LoxError.report(linenumber, "", message)
