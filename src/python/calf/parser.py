"""
The Calf parser.
"""

from collections import namedtuple

from calf.lexer import lex_buffer, lex_file
from calf.grammar import MATCHING, WHITESPACE_TYPES
from calf.token import *


def mk_list(contents, open=None, close=None):
    return CalfListToken(
        "LIST", contents, open.source, open.start_position, close.start_position
    )


def mk_sqlist(contents, open=None, close=None):
    return CalfListToken(
        "SQLIST", contents, open.source, open.start_position, close.start_position
    )


def mk_dict(contents, open=None, close=None):
    return CalfDictToken(
        "DICT",
        dict(*list(zip(contents[::2], contents[1::2]))),
        open.source,
        open.start_position,
        close.start_position,
    )


MATCHING_CTOR = {
    # Compound tokens
    "PAREN_LEFT": mk_list,
    "BRACE_LEFT": mk_dict,
    "BRACKET_LEFT": mk_sqlist,
    # Singleton tokens
    "INTEGER": CalfIntegerToken,
    "FLOAT": CalfFloatToken,
    "STRING": CalfStrToken,
}


ParseStackElement = namedtuple(
    "ParseStackElement", ["buffer", "open_token", "close_type", "ctor"]
)


class CalfParseError(Exception):
    """
    Base class for representing errors encountered parsing.
    """


class CalfUnexpectedCloseParseError(CalfParseError):
    """
    Represents encountering an unexpected close token.
    """

    def __init__(self, message, token, expecting=None, expecting_position=None):
        super(CalfParseError, self).__init__()
        self.message = message
        self.token = token
        self.expecting = expecting
        self.expecting_position = expecting_position

    def __str__(self):
        return "Parse error at %r: %s" % (self.token.position, self.message,)


class CalfMissingCloseParseError(CalfParseError):
    """
    Represents a failure to encounter an expected close token.
    """

    def __init__(self, expected_close_token, open_token):
        super(CalfMissingCloseParseError, self).__init__()
        self.expected_close_token = expected_close_token
        self.open_token = open_token

    def __str__(self):
        return "Parse error: expected %s starting from %r, got end of file." % (
            self.expected_close_token,
            self.open_token.position,
        )


def parse_stream(stream):
    """
    Parses a token stream, producing a lazy sequence of all read top level forms.
    """

    # `stack` is a list (used as a stack) of tuples (buffer, close, ctor).
    # Tokens are accumulated in a buffer, until a matching close token is
    # found.
    #
    # This is a very simple parser intended to support only the simplest of
    # syntactic constructs while providing actually quite good parse error
    # traceback.

    stack = []
    tokens = None

    for token in stream:
        # Case 1 - we got the close character we were looking for.
        if stack and token.type == stack[-1].close_type:
            # Extract the stack element
            el = stack.pop()

            # Call the ctor
            yield el.ctor(el.buffer, open=el.open_token, close=token)

            # Fix the tokens reference
            if stack:
                tokens = stack[-1].tokens

            else:
                tokens = None

        # Case 2 - we got a new open token
        elif token.type in MATCHING:
            # Create a new tokens array
            tokens = list()

            # Create & push a new stack element
            stack.append(
                ParseStackElement(
                    tokens, token, MATCHING[token.type], MATCHING_CTOR[token.type]
                )
            )

        # Case 3 - we got an unexpected close
        elif token.type in list(MATCHING.values()):
            # FIXME: recover the parser if possible?
            raise CalfParseError("Unexpected close token", token)

        # Case 4 - we got whitespace
        elif token.type in WHITESPACE_TYPES:
            # FIXME: don't discard whitespace all the time.
            #
            # It would be awesome if whitespace & comments were node metadata
            # in the style of the MSFT CODE editor.
            continue

        # Case 5 - we got an internal token
        elif stack and tokens is not None:
            tokens.append(token)

        # Case 6 - token with transformer
        elif token.type in MATCHING_CTOR:
            yield MATCHING_CTOR[token.type](token)

        # Case 7 - top level token with no transformer
        else:
            yield token

    # We've run out of tokens to scan and were still looking for something
    if stack:
        el = stack.pop()  # we don't care
        raise CalfMissingCloseParseError(el.close_type, el.open_token)


def parse_buffer(buffer):
    """
    Parses a buffer, producing a lazy sequence of all read top level forms.

    Propagates all errors.
    """

    for atom in parse_stream(lex_buffer(buffer)):
        yield atom


def parse_file(file):
    """
    Parses a file, producing a lazy sequence of all read top level forms.
    """

    for atom in parse_stream(lex_file(file)):
        yield atom
