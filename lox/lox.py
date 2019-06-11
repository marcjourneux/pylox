import argparse
from lox.scanner import scan_tokens
from lox.parser import Parser
from lox.astprinter import PrinterVisitor
from lox.expr import Expr
from lox.interpreter import Interpreter
from lox.resolver import Resolver
from lox.error import LoxError
from lox.tokentype import TokensDic as Tk


class Lox:
    def __init__(self):
        self.interpreter = Interpreter()
        self.error = LoxError()

    def run_prompt(self):
        errors = []
        s = input("lox >")
        if s != "exit":
            if s[len(s)-1] is not ";":
                s = s + ";"
            self.run(s, errors)
            self.run_prompt()

    def run_files(self, files):
        errors = []
        for file in files:
            try:
                with open(file, 'r') as f:
                    source = f.read()
                    lox.run(source, errors)
            except:
                print("cannot read file {}".format(file))

    def run(self, source, errors):
        #print("source : \n{}".format(source))
        tokens = []
        statements = []
        scan_tokens(
            source, {'start': 0, 'current': 0, 'line': 1}, tokens, errors)
        if len(tokens) is 1:
            if tokens[0].type is Tk.EOF:
                LoxError.error(tokens[0], "Source file is empty.")
        parser = Parser(tokens)
        # print("Tokens:\n")
        # for t in tokens:
        #     print(t)
        #print("Lox: ready to parse")
        statements = parser.parse()
        #print("Lox: ready to resolve")
        resolver = Resolver(self.interpreter)
        resolver.resolvelist(statements)
        if LoxError.haderror:
            print("Syntax errors detected during compilation")
            return
        #print("Lox: ready to interpret")
        self.interpreter.interpret(statements)


if __name__ == "__main__":
    """ Main for compiling Lox language.

    no arguments given start the REPL,
    you can input a list of files otherwise."""
    parser = argparse.ArgumentParser(description='Compile lox file')
    parser.add_argument('files', nargs='*',
                        help='lox source file')
    args = parser.parse_args()
    lox = Lox()
    if args.files:
        lox.run_files(args.files)
    else:
        lox.run_prompt()
