from lox.error import InterpreterError
from lox.token import LoxToken


class LoxInstance():
    """Class for the runtime representation of the Lox instance"""

    def __init__(self, xclass):
        self.xclass = xclass
        self.propertymap = {}

    def get_property(self, name: LoxToken) -> object:
        # is it a property ?
        if name.lexeme in self.propertymap:
            return self.propertymap[name.lexeme]
        # or a class method ?
        method = self.xclass.findmethod(name)
        if method is not None:
            return method.bind(self)
        if name.lexeme in self.xclass.methods:
            method = self.xclass.methods[name.lexeme]

        raise InterpreterError(name, "Undefined property.")

    def set_property(self, name: LoxToken, value):
        self.propertymap[name.lexeme] = value

    def __str__(self):
        return self.xclass.name
