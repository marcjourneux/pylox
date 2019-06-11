# Definition of the LoxCallable classfrom

from lox.environment import Environment
from typing import List
from lox.stmt import Function
from lox.expr import FunctionExp
from lox.instance import LoxInstance
from lox.tokentype import TokensDic as Tk
from lox.constants import LoxConstant
from lox.error import ReturnException
from lox.functiontypes import FunctionType


class LoxCallable:
    """Superclass for runtime of callable objects."""

    def call(self, interpreter, arguments: List[object]):
        pass

    def arity(self) -> int:
        pass


class LoxFunction(LoxCallable):
    """Runtime for function."""

    def __init__(self, name: "LoxToken", fundec: FunctionExp, closure):
        self.name = name
        self.fundec = fundec
        self.call_env = None
        self.closure = closure

    def arity(self) -> int:
        return len(self.fundec.params)

    def call(self, interpreter, arguments: List[object]):
        # create an environment for this call, inside the calling env
        self.call_env = Environment(self.closure)
        # Add the parameters to this env with their "calling" value
        for i in range(len(arguments)):
            self.call_env.define(self.fundec.params[i].lexeme, arguments[i])
        # call the function: execute the block wit the current env
        try:
            interpreter.executeblock(self.fundec.body, self.call_env)
        except ReturnException as exc:
            if self.fundec.functiontype is FunctionType.INIT:
                return self.closure.getat(0, Tk.lexeme_from_type[Tk.THIS])
            return exc.value

    def bind(self, instance):
        """Bind the instance to the method."""
        this_env = Environment(self.closure)
        this_env.define(Tk.lexeme_from_type[Tk.THIS], instance)
        return LoxFunction(self.name, self.fundec, this_env)

    def __str__(self):
        if self.name is None:
            return "<function>"
        else:
            return "<function: " + self.name.lexeme + ">"


class LoxClass(LoxCallable):
    """Class for the runtime representation of the Lox class"""

    def __init__(self, name, superclass, methods: List[FunctionExp]):
        self.name = name
        self.superclass = superclass
        self.methods = {}
        for method in methods:
            self.methods[method.name.lexeme] = method

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments: List[object]):
        instance = LoxInstance(self)
        initializer = self.methods.get(LoxConstant.init_method)
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        initializer = self.methods.get(LoxConstant.init_method)
        if initializer:
            return initializer.arity()
        return 0

    def findmethod(self, name):
        method = self.methods.get(name.lexeme)
        if method is not None:
            return method
        if self.superclass is not None:
            return self.superclass.findmethod(name)
        return None
