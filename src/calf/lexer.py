"""
Calf lexer.

Provides machinery for lexing sources of text into sequences of tokens with textual information, as
well as buffer position information appropriate for either full AST parsing, lossless syntax tree
parsing, linting or other use.
"""

import StringIO
import re

from calf.token import CalfToken
from calf.reader import PeekPosReader
from calf.grammar import TOKENS
from calf.util import *


class CalfLexer():
    """
    Lexer object.

    Wraps something you can read characters from, and presents a lazy sequence of Token objects.

    Raises ValueError at any time due to either a conflict in the grammar being lexed, or incomplete
    input. Exceptions from the backing reader object are not masked.
    """

    def __init__(self, stream, source=None, metadata=None, tokens=TOKENS):
        """FIXME"""

        self._stream = PeekPosReader(stream) if not isinstance(stream, PeekPosReader) else stream
        self.source = source
        self.metadata = metadata or {}
        self.tokens = tokens

    def next(self):
        """
        Tries to scan the next token off of the backing stream.

        Starting with a list of all available tokens, an empty buffer and a single new character
        peeked from the backing stream, reads more character so long as adding the next character
        still leaves one or more possible matching "candidates" (token patterns).

        When adding the next character from the stream would build an invalid token, a token of the
        resulting single candidate type is generated.  If multiple candidates cannot be
        distinguished between, a ValueError is produced.

        At the end of input, if we have a single candidate remaining, a final token of that type is
        generated.  Otherwise we are in an incomplete input state either due to incomplete input or
        a grammar conflict.
        """

        buffer = ""
        candidates = self.tokens
        position, chr = self._stream.peek()

        while chr:
            print "%r %r %r" % (buffer, chr, candidates)

            if not candidates:
                raise ValueError("Entered invalid state - no candidates!")

            buff2 = buffer + chr
            can2 = [t for t in candidates if re_whole_match(re_mem(t[0]), buff2)]

            # Try to include the last read character to support longest-wins grammars
            if not can2:
                if len(candidates) == 1:
                    pat, type = candidates[0]
                    groups = re.match(re.compile(pat), buffer).groupdict()
                    groups.update(self.metadata)
                    return CalfToken(type, buffer, self.source, position, groups)

                elif buffer:
                    raise ValueError(
                        "Buffer %r is ambiguous between token types\n- %s" % (
                            buffer, '\n- '.join(type for pat, type in self.tokens)))

            else:
                # Update the buffers
                buffer = buff2
                candidates = can2

                # consume the 'current' character for side-effects
                self._stream.read()

                # set chr to be the next peeked character
                _, chr = self._stream.peek()

        if len(candidates) == 1:
            pat, type = candidates[0]
            groups = re.match(re.compile(pat), buffer).groupdict()
            groups.update(self.metadata)
            return CalfToken(type, buffer, self.source, position, groups)

        else:
            raise ValueError("Encountered end of buffer with incomplete token %r" % (buffer,))

    def __iter__(self):
        """
        Scans tokens out of the character stream.

        May raise ValueError if there is either an issue with the grammar or the input.
        Will not mask any exceptions from the backing reader.
        """

        # While the character stream isn't empty
        while self._stream.peek()[1] != '':
            yield self.next()


def lex_file(path):
    """
    Returns the lazy sequence of tokens resulting from lexing all text in the named file.
    """

    return CalfLexer(open(path, 'r'), path, metadata)


def lex_buffer(buffer, metadata=None):
    """
    Returns the lazy sequence of tokens resulting from lexing all the text in a buffer.
    """

    return CalfLexer(StringIO.StringIO(buffer), "<Buffer>", metadata)


if __name__ == "__main__":
    pass
