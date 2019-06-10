import lox.callable
from typing import List
import time


class Clock(lox.callable.LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: List[object]) -> object:
        return time.clock()

    def __str__(self):
        return "<clock: native function>"
