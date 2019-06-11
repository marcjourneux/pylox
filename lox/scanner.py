#
# Scanner for the lox compiler
#
from lox.tokentype import TokensDic
from lox.token import LoxToken
from lox.error import LoxError


def is_at_end(source, positions):
    return positions['current'] >= len(source)


def advance(source, positions):
    if not is_at_end(source, positions):
        positions['current'] += 1
        return source[positions['current']-1:positions['current']]
    else:
        return ""


def advance_eol(source, positions):
    c = advance(source, positions) != '\n'
    while c != '\n' and c != "":
        c = advance(source, positions)


def peek(source, positions):
    """Return the current char without moving forward."""
    if positions['current'] >= len(source):
        return ""
    else:
        return source[positions['current']:positions['current']+1]


def peek_next(source, positions):
    """Return the next char without moving forward."""
    if positions['current']+1 >= len(source):
        return ""
    else:
        return source[positions['current']+1:positions['current']+2]


def string(source, positions):
    """Scan strings."""
    while not is_at_end(source, positions) and peek(source, positions) != '"':
        if peek(source, positions) == '\n':
            positions['line'] += 1
        advance(source, positions)
    if is_at_end(source, positions):
        LoxError.error(positions['line'], "String is not ended with quotes.")
        return None
    # Closing quote
    else:
        advance(source, positions)
        # return string without quotes
        return source[positions['start']+1:positions['current']-1]


def is_digit(c):
    try:
        int(c)
        return True
    except ValueError:
        return False


def number(source, positions):
    """Scan numbers."""
    while is_digit(peek(source, positions)):
        advance(source, positions)

    if peek(source, positions) == '.':
        if is_digit(peek_next(source, positions)):
            advance(source, positions)
        while is_digit(peek(source, positions)):
            advance(source, positions)

    return float(source[positions['start']:positions['current']])


def is_alpha(c):
    return c.isalpha() or c == "_"


def is_alphanum(c):
    return c.isalpha() or c == "_" or is_digit(c)

# Identifier is starting with a letter and contains alphanum
# and underscore


def identifier(source, positions):
    """Scan identifiers: they should starts with a letter and contains alphanum and underscore."""
    while is_alphanum(peek(source, positions)):
        advance(source, positions)
    return source[positions['start']:positions['current']]


def scan_token(source, positions, tokens, errors):
    """Main method to scan token."""
    positions['start'] = positions['current']
    c = advance(source, positions)
    #
    # Single character loxtoken
    if c in TokensDic.singlechartoken:
        tokens.append(LoxToken(TokensDic.type_from_lexeme[c], c,
                               "", positions['line']))
    #
    # LoxToken that may be composed of 2 Char (>, !, =, <, /)
    elif c in TokensDic.doublechartoken:
        follow = peek(source, positions)
        if c+follow in TokensDic.linecommenttoken:
            advance_eol(source, positions)
        elif c+follow in TokensDic.composedchartoken:
            advance(source, positions)
            tokens.append(LoxToken(TokensDic.type_from_lexeme[c+follow], c+follow,
                                   "", positions['line']))
        else:
            tokens.append(LoxToken(TokensDic.type_from_lexeme[c], c,
                                   "", positions['line']))
    # Spaces and newline
    elif c.isspace():
        if '\n' in c:
            positions['line'] += 1
    # String literals
    elif c == '"':
        value = string(source, positions)
        if value:
            tokens.append(LoxToken(TokensDic.STRING, "",
                                   value, positions['line']))
    # Numbers
    elif is_digit(c):
        num = number(source, positions)
        tokens.append(LoxToken(TokensDic.NUMBER, '', num, positions['line']))

    # Identifiers and reserverd words
    elif is_alpha(c):
        value = identifier(source, positions)
        # check if we have an reserved keyword
        if value in TokensDic.reservedkeywords:
            tokens.append(LoxToken(TokensDic.type_from_lexeme[value],
                                   value, "", positions['line']))
        else:
            tokens.append(LoxToken(TokensDic.IDENTIFIER,
                                   value, "", positions['line']))


def scan_tokens(source, positions, tokens, errors):
    while positions['current'] < len(source):
        positions['start'] = positions['current']
        scan_token(source, positions, tokens, errors)

    tokens.append(LoxToken(TokensDic.EOF, "", "", positions['line']))
