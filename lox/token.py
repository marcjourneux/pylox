# Definition of the LoxToken class
class LoxToken:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        string = "{0}\t\t{1}\t\t{2}".format(
            self.type, str(self.lexeme), str(self.literal))
        return string
