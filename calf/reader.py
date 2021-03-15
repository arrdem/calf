"""The Calf reader

Unlike the lexer and parser which are mostly information preserving, the reader
is designed to be a somewhat pluggable structure for implementing transforms and
discarding information.

"""

from typing import *

from calf.lexer import lex_buffer, lex_file
from calf.parser import parse_stream
from calf.token import *

DEFAULT_DISPATCH = {
    "LIST": lambda t: t.value,
    "SQLIST": lambda t: t.value,
    "DICT": lambda t: t.value,
}


class CalfReader(object):
    def make_keyword(self, v: str) -> Any:
        return v

    def handle_keyword(self, t: CalfToken) -> Any:
        """Convert a token to an Object value for a symbol.

        Implementations could convert kws to strings, to a dataclass of some
        sort, use interning, or do none of the above.

        """

        return self.make_keyword(t.value)

    def make_symbol(self, v: str) -> Any:
        return v

    def handle_symbol(self, t: CalfToken) -> Any:
        """Convert a token to an Object value for a symbol.

        Implementations could convert syms to strings, to a dataclass of some
        sort, use interning, or do none of the above.

        """

        return self.make_symbol(t.value)

    def handle_dispatch(self, t: CalfDispatchToken) -> Any:
        """Handle a #foo <> dispatch token.

        Implementations may choose how dispatch is mapped to values, for
        instance by imposing a static mapping or by calling out to runtime state
        or other data sources to implement this hook. It's intended to be an
        open dispatch mechanism, unlike the others which should have relatively
        defined behavior.

        The default implementation simply preserves the dispatch token.

        """

        return t

    def handle_meta(self, t: CalfMetaToken) -> Any:
        """Handle a ^<> <> so called 'meta' token.

        Implementations may choose how to process metadata, discarding it or
        consuming it somehow.

        The default implementation simply discards the tag value.

        """

        return self.read1(t.value)

    def handle_quote(self, t: CalfQuoteToken) -> Any:
        """Handle a 'foo quote form."""

        return [self.make_symbol("quote"), self.read1(t.value)]

    def read1(self, t: CalfToken) -> Any:
        # Note: 'square' and 'round' lists are treated the same. This should be
        # a hook. Should {} be a "list" too until it gets reader hooked into
        # being a mapping or a set?
        if isinstance(t, CalfListToken):
            return list(self.read(t.value))

        elif isinstance(t, CalfDictToken):
            return {self.read1(k): self.read1(v)
                    for k, v in t.items()}

        elif isinstance(t, CalfQuoteToken):
            return self.handle_quote(t)

        # Stuff with real factories
        elif isinstance(t, CalfKeywordToken):
            return self.handle_keyword(t)

        elif isinstance(t, CalfSymbolToken):
            return self.handle_symbol(t)

        # Terminals
        elif isinstance(t, (CalfStrToken, CalfFloatToken, CalfIntegerToken)):
            return t.value

        else:
            raise ValueError(f"Unsupported token type {t!r} ({type(t)})")

    def read(self, stream):
        """Given a sequence of tokens, read 'em."""

        for t in stream:
            yield self.read1(t)


def read_stream(stream,
                reader: CalfReader = None):
    """Read from a stream of parsed tokens.

    """

    reader = reader or CalfReader()
    yield from reader.read(stream)


def read_buffer(buffer):
    """Read from a buffer, producing a lazy sequence of all top level forms.

    """

    yield from read_stream(parse_stream(lex_buffer(buffer)))


def read_file(file):
    """Read from a file, producing a lazy sequence of all top level forms.

    """

    yield from read_stream(parse_stream(lex_file(file)))


def main():
    """A CURSES application for using the reader."""

    from calf.curserepl import curse_repl

    def handle_buffer(buff, count):
        return list(read_stream(parse_stream(lex_buffer(buff, source=f"<Example {count}>"))))

    curse_repl(handle_buffer)
