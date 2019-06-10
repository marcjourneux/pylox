

class TokensDefinition:
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    COMMA = "COMMA"
    DOT = "DOT"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SEMICOLON = "SEMICOLON"
    STAR = "STAR"
    BANG = "BANG"
    BANG_EQUAL = "BANG_EQUAL"
    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    SLASH = "SLASH"
    LINE_COMMENT = "LINE_COMMENT"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    AND = "AND"
    BREAK = "BREAK"
    CLASS = "CLASS"
    ELSE = "ELSE"
    FALSE = "FALSE"
    FUN = "FUN"
    FOR = "FOR"
    IF = "IF"
    NIL = "NIL"
    OR = "OR"
    PRINT = "PRINT"
    RETURN = "RETURN"
    SUPER = "SUPER"
    THIS = "THIS"
    TRUE = "TRUE"
    VAR = "VAR"
    WHILE = "WHILE"
    EOF = "EOF"

    def __init__(self):
        tokens = {
            self.LEFT_PAREN: ("(", 'single'),
            self.RIGHT_PAREN: (")", 'single'),
            self.LEFT_BRACE: ('{', 'single'),
            self.RIGHT_BRACE: ('}', 'single'),
            self.COMMA: (',', 'single'),
            self.DOT: ('.', 'single'),
            self.MINUS: ('-', 'single'),
            self.PLUS: ('+', 'single'),
            self.SEMICOLON: (';', 'single'),
            self.STAR: ('*', 'single'),
            self.BANG: ('!', 'double'),
            self.BANG_EQUAL: ('!=', 'composed'),
            self.EQUAL: ('=', 'double'),
            self.EQUAL_EQUAL: ('==', 'composed'),
            self.GREATER: ('>', 'double'),
            self.GREATER_EQUAL: ('>=', 'composed'),
            self.LESS: ('<', 'double'),
            self.LESS_EQUAL: ('<=', 'composed'),
            self.SLASH: ('/', 'double'),
            self.LINE_COMMENT: ('//', 'linecomment'),
            self.IDENTIFIER: (None, None),
            self.STRING: (None, None),
            self.NUMBER: (None, None),
            self.AND: ('and', 'reserved'),
            self.BREAK: ('break', 'reserved'),
            self.CLASS: ('class', 'reserved'),
            self.ELSE: ('else', 'reserved'),
            self.FALSE: ('false', 'reserved'),
            self.FUN: ('fun', 'reserved'),
            self.FOR: ('for', 'reserved'),
            self.IF: ('if', 'reserved'),
            self.NIL: ('nil', 'reserved'),
            self.OR: ('or', 'reserved'),
            self.PRINT: ('print', 'reserved'),
            self.RETURN: ('return', 'reserved'),
            self.SUPER: ('super', 'reserved'),
            self.THIS: ('this', 'reserved'),
            self.TRUE: ('true', 'reserved'),
            self.VAR: ('var', 'reserved'),
            self.WHILE: ('while', 'reserved'),
            self.EOF: (None, None)
        }
        self.types = []
        self.type_from_lexeme = {}
        self.type_from_token = {}
        self.singlechartoken = {}
        self.doublechartoken = {}
        self.composedchartoken = {}
        self.mulchartoken = {}
        self.linecommenttoken = {}
        self.reservedkeywords = {}
        self.lexeme_from_type = {}
        # Build the list of possible token

        for key, t in tokens.items():
            self.types.append(key)
            lexeme = t[0]

            if t[0] is not None:
                self.type_from_lexeme[lexeme] = key
                self.lexeme_from_type[key] = lexeme
            if t[1] == 'single':
                self.singlechartoken[lexeme] = key
            if t[1] == 'double':
                self.doublechartoken[lexeme] = key
            if t[1] == 'composed':
                self.composedchartoken[lexeme] = key
            if t[1] == 'multiple':
                self.mulchartoken[lexeme] = key
            if t[1] == 'linecomment':
                self.linecommenttoken[lexeme] = key
            if t[1] == 'reserved':
                self.reservedkeywords[lexeme] = key


TokensDic = TokensDefinition()
