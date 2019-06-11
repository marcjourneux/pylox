from lox.error import LoxRuntimeError
from lox.token import LoxToken


class Environment:
    """Managing scopes working with interpreter."""

    def __init__(self, enclosing_env=None):
        self.__varmap = {}
        self.enclosing = enclosing_env

    def assign(self, token: LoxToken, value):
        if token.lexeme in self.__varmap:
            self.__varmap[token.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(token, value)
            return

        raise LoxRuntimeError(
            token, "Undefined variable " + token.lexeme + " " + str(token))

    def ancestor(self, distance: int) -> 'Environment':
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def define(self, varname, value):
        self.__varmap[varname] = value

    def defineat(self, distance, varname, value):
        self.ancestor(distance).__varmap[varname] = value

    def get(self, name: "LoxToken or str") -> object:
        varname = None
        if isinstance(name, LoxToken):
            varname = name.lexeme
        elif isinstance(name, str):
            varname = name
        if varname in self.__varmap:
            return self.__varmap[varname]
        if self.enclosing is not None:
            return self.enclosing.get(varname)

        raise LoxRuntimeError(
            name, "Undefined variable '" + varname + "'.")

    def getat(self, distance, name):
        varname = None
        if isinstance(name, LoxToken):
            varname = name.lexeme
        elif isinstance(name, str):
            varname = name
        if varname in self.ancestor(distance).__varmap:
            return self.ancestor(distance).__varmap[varname]
        raise LoxRuntimeError(
            name, "Undefined variable '" + varname + "'.")
