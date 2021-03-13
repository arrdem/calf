"""
The Calf parser.
"""

from collections import namedtuple
from itertools import tee
import logging
import sys
from typing import NamedTuple, Callable

from calf.lexer import CalfLexer, lex_buffer, lex_file
from calf.grammar import MATCHING, WHITESPACE_TYPES
from calf.token import *


log = logging.getLogger(__name__)


def mk_list(contents, open=None, close=None):
    return CalfListToken(
        "LIST", contents, open.source, open.start_position, close.start_position
    )


def mk_sqlist(contents, open=None, close=None):
    return CalfListToken(
        "SQLIST", contents, open.source, open.start_position, close.start_position
    )


def pairwise(l: list) -> iter:
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    return zip(l[::2], l[1::2])


def mk_dict(contents, open=None, close=None):
    return CalfDictToken(
        "DICT",
        list(pairwise(contents)),
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


class ParseStackElement(NamedTuple):
    """The parser maintains an internal push-pop top stack used to build up tokens.

    Parse stack elements track all the component subtokens parsed so far, the
    close token which is being awaited and the constructor which will
    manufacture a "complete" token given the contents, open and close tokens.

    """
    tokens: list
    open_token: CalfToken
    close_type: str
    ctor: Callable[[list, CalfToken, CalfToken], CalfToken]


class CalfParseError(Exception):
    """
    Base class for representing errors encountered parsing.
    """


class CalfUnexpectedCloseParseError(CalfParseError):
    """
    Represents encountering an unexpected close token.
    """

    def __init__(self, token, matching_open=None):
        super(CalfParseError, self).__init__()
        self.token = token
        self.matching_open = matching_open

    def __str__(self):
        msg = f"Parse error: encountered unexpected closing {self.token!r}"
        if self.matching_open:
            msg += " which appears to match {self.matching_open!r}"
        return msg


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
            self.open_token.start_position,
        )


def parse_stream(stream,
                 discard_whitespace: bool = True):
    """Parses a token stream, producing a lazy sequence of all read top level forms.

    If `discard_whitespace` is truthy, then no WHITESPACE tokens will be emitted
    into the resulting parse tree. Otherwise, WHITESPACE tokens will be
    included. Whether WHITESPACE tokens are included or not, the tokens of the
    tree will reflect original source locations.

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
            token = el.ctor(el.tokens, open=el.open_token, close=token)

            # Fix the tokens reference
            if stack:
                tokens = stack[-1].tokens

            else:
                tokens = None

            # Figure out where the new token goes
            if stack and tokens is not None:
                tokens.append(token)

            elif not stack:
                yield token

            else:
                raise CalfParseError(f"Illegal state! considering {token}, stack {stack} and tokens {tokens}")

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
        elif (token.type in list(MATCHING.values())
              and (open_token := next((e for e in reversed(stack) if e.close_type == token.type), None))):
            raise CalfParseError(token, open_token)

        # Case 4 - we got whitespace
        elif token.type in WHITESPACE_TYPES and discard_whitespace:
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


def parse_buffer(buffer,
                 discard_whitespace=True):
    """
    Parses a buffer, producing a lazy sequence of all read top level forms.

    Propagates all errors.
    """

    for atom in parse_stream(lex_buffer(buffer), discard_whitespace):
        yield atom


def parse_file(file):
    """
    Parses a file, producing a lazy sequence of all read top level forms.
    """

    for atom in parse_stream(lex_file(file)):
        yield atom


def main():
    """A CURSES application for using the parser."""

    from calf.curserepl import curse_repl

    def handle_buffer(buff, count):
        return list(parse_stream(lex_buffer(buff, source=f"<Example {count}>"), discard_whitespace=False))

    curse_repl(handle_buffer)
