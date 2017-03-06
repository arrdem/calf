"""
Calf lexer.

Lexes sources of text into
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

    Wraps something you can read characters from, and presents a sequence of Token objects.

    FIXME: how to handle remaining characters?
    """

    def __init__(self, stream, source=None, metadata=None, tokens=TOKENS):
        """FIXME"""

        self._stream = PeekPosReader(stream) if not isinstance(stream, PeekPosReader) else stream
        self.source = source
        self.metadata = metadata or {}
        self.tokens = tokens

    def __next_token__(self):
        """FIXME"""

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
            if not can2 and len(candidates) == 1:
                pat, type = candidates[0]
                groups = re.match(re.compile(pat), buffer).groupdict()
                groups.update(self.metadata)
                return CalfToken(type, buffer, self.source, position, groups)

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
        """Scans tokens out of the character stream."""

        # While the character stream isn't empty
        while self._stream.peek()[1] != '':
            yield self.__next_token__()


def lex_file(path):
    """Lexes an entire file from a path."""

    return CalfLexer(open(path, 'r'), path, metadata)


def lex_buffer(buffer, metadata=None):
    """Lexes an entire buffer"""

    return CalfLexer(StringIO.StringIO(buffer), "<Buffer>", metadata)


if __name__ == "__main__":
    pass
