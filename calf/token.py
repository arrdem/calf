"""
Tokens.

The philosophy here is that to the greatest extent possible we want to preserve lexical (source)
information about indentation, position and soforth.  That we have to do so well mutably is just a
pain in the ass and kinda unavoidable.

Consequently, this file defines classes which wrap core Python primitives, providing all the usual
bits in terms of acting like values, while preserving fairly extensive source information.
"""


class CalfToken:
    """
    Token object.

    The result of reading a token from the source character feed.
    Encodes the source, and the position in the source from which it was read.
    """

    def __init__(self, type, value, source, start_position, more):
        self.type = type
        self.value = value
        self.source = source
        self.start_position = start_position
        self.more = more if more is not None else {}

    def __repr__(self):
        return "<CalfToken:%s %r %r@%r:%r %r>" % (
            self.type,
            self.value,
            self.source,
            self.line,
            self.column,
            self.more,
        )

    def __str__(self):
        return self.value

    @property
    def offset(self):
        if self.start_position is not None:
            return self.start_position.offset

    @property
    def line(self):
        if self.start_position is not None:
            return self.start_position.line

    @property
    def column(self):
        if self.start_position is not None:
            return self.start_position.column


class CalfBlockToken(CalfToken):
    """
    (Block) Token object.

    The base result of parsing a token with a start and an end position.
    """

    def __init__(self, type, value, source, start_position, end_position, more):
        CalfToken.__init__(self, type, value, source, start_position, more)
        self.end_position = end_position


class CalfListToken(CalfBlockToken, list):
    """
    (list) Token object.

    The final result of reading a parens list through the Calf lexer stack.
    """

    def __init__(self, type, value, source, start_position, end_position):
        CalfBlockToken.__init__(
            self, type, value, source, start_position, end_position, None
        )
        list.__init__(self, value)


class CalfDictToken(CalfBlockToken, dict):
    """
    (dict) Token object.

    The final(ish) result of reading a braces list through the Calf lexer stack.
    """

    def __init__(self, type, value, source, start_position, end_position):
        CalfBlockToken.__init__(
            self, type, value, source, start_position, end_position, None
        )
        dict.__init__(self, value)


class CalfIntegerToken(CalfToken, int):
    """
    (int) Token object.


    The final(ish) result of reading an integer.
    """

    def __new__(cls, value):
        return int.__new__(cls, value.value)

    def __init__(self, value):
        CalfToken.__init__(
            self,
            value.type,
            value.value,
            value.source,
            value.start_position,
            value.more,
        )


class CalfFloatToken(CalfToken, float):
    """
    (int) Token object.


    The final(ish) result of reading a float.
    """

    def __new__(cls, value):
        return float.__new__(cls, value.value)

    def __init__(self, value):
        CalfToken.__init__(
            self,
            value.type,
            value.value,
            value.source,
            value.start_position,
            value.more,
        )


class CalfStrToken(CalfToken, str):
    """
    (str) Token object.


    The final(ish) result of reading a string.
    """

    def __new__(cls, value):
        buff = value.value

        if buff.startswith('"""') and not buff.endswith('"""'):
            raise ValueError('Unterminated tripple quote string')

        elif buff.startswith('"') and not buff.endswith('"'):
            raise ValueError('Unterminated quote string')

        elif not buff.startswith('"') or buff == '"' or buff == '"""':
            raise ValueError('Illegal string')

        if buff.startswith('"""'):
            buff = buff[3:-3]
        else:
            buff = buff[1:-1]

        buff = buff.encode("utf-8").decode("unicode_escape")  # Handle escape codes

        return str.__new__(cls, buff)

    def __init__(self, value):
        CalfToken.__init__(
            self,
            value.type,
            value.value,
            value.source,
            value.start_position,
            value.more,
        )
