"""
Tokens.

"""


class CalfToken():
    """
    Token object.

    The result of reading a token from the source character feed.
    Encodes the source, and the position in the source from which it was read.
    """

    def __init__(self, type, value, source, position, more):
        self.type = type
        self.value = value
        self.source = source
        self.position = position
        self.more = more

    def __repr__(self):
        return "<CalfToken %r %r %r@%r:%r %r>" % (
            self.type, self.value, self.source, self.line, self.column, self.more
        )

    def __str__(self):
        return self.value

    @property
    def offset(self):
        return self.position.offset

    @property
    def line(self):
        return self.position.line

    @property
    def column(self):
        return self.position.column
