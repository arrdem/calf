"""
The elements of the Calf grammar. Used by the lexer.
"""

WHITESPACE = r'\n\r\s,'

DELIMS = r'%s\[\]\(\)\{\}:;#^"\'' % (WHITESPACE,)

SIMPLE_SYMBOL = r'([^{ds}\-\+\d][^{ds}]*)|([^{ds}\d]+)'.format(ds=DELIMS)

SYMBOL_PATTERN = r'(((?P<namespace>{ss})/)?(?P<name>{ss}))'.format(ss=SIMPLE_SYMBOL)

SIMPLE_INTEGER = r'[+-]?\d*'

FLOAT_PATTERN = r'(?P<body>({i})(\.(\d*))?)?([eE](?P<exponent>{i}))?'.format(i=SIMPLE_INTEGER)

TOKENS = [
    # Paren (noral) lists
    (r'\(', "PAREN_LEFT",),
    (r'\)', "PAREN_RIGHT",),

    # Bracket lists
    (r'\[', "BRACKET_LEFT",),
    (r'\]', "BRACKET_RIGHT",),

    # Brace lists (maps)
    (r'\{', "BRACE_LEFT",),
    (r'\}', "BRACE_RIGHT",),
    (r'\^', "META",),
    (r"'", "SINGLE_QUOTE",),
    (r'"', "DOUBLE_QUOTE",),
    (r'#', "MACRO_DISPATCH",),

    # Symbols
    (SYMBOL_PATTERN, "SYMBOL",),

    # Numbers
    (SIMPLE_INTEGER, "INTEGER",),
    (FLOAT_PATTERN, "FLOAT",),

    # Keywords
    #
    # Note: this is a dirty f'n hack in that in order for keywords to work, ":"
    # has to be defined to be a valid keyword.
    (r':' + SYMBOL_PATTERN + "?", "KEYWORD",),

    # Whitespace
    #
    # Note that the whitespace token will contain at most one newline
    (r'[{ws}]*'.format(ws=WHITESPACE), "WHITESPACE",),

    # Comment
    (r';(([^\n\r]*)(\n\r?)?)', "COMMENT",),

    # Strings
    (r'"(?P<body>(?:[^\"]|\.)*)"', "STRING")
]

MATCHING = {
    "PAREN_LEFT": "PAREN_RIGHT",
    "BRACKET_LEFT": "BRACKET_RIGHT",
    "BRACE_LEFT": "BRACE_RIGHT"
}


WHITESPACE_TYPES = {
    'WHITESPACE', 'COMMENT'
}
