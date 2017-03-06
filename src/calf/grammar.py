"""
The elements of the Calf grammar. Used by the lexer.
"""

SIMPLE_SYMBOL = r'[^\[\]\(\)\{\}:;#^\s\d"\']+'

SYMBOL_PATTERN = r'(((?P<namespace>{ss})/)?(?P<name>{ss}))'.format(ss=SIMPLE_SYMBOL)

SIMPLE_INTEGER = r'[+-]?\d+'

FLOAT_PATTERN = r'(?P<body>({i})(\.(\d*))?)?([eE](?P<exponent>{i}))?'.format(i=SIMPLE_INTEGER)

TOKENS = [
    # Paren (noral) lists
    (r'\(', 'PAREN_LEFT',),
    (r'\)', 'PAREN_RIGHT',),

    # Bracket lists
    (r'\[', 'BRACKET_LEFT',),
    (r'\]', 'BRACKET_RIGHT',),

    # Brace lists (maps)
    (r'\{', 'BRACE_LEFT',),
    (r'\}', 'BRACE_RIGHT',),

    (r'\^', 'META',),
    (r"'", "SINGLE_QUOTE",),
    (r'"', 'DOUBLE_QUOTE',),
    (r'#', 'MACRO_DISPATCH',),

    # Numbers
    (FLOAT_PATTERN, 'FLOAT',),
    (SIMPLE_INTEGER, 'INTEGER',),

    # Keywords
    #
    # Note: this is a dirty f'n hack in that in order for keywords to work, ":"
    # has to be defined to be a valid keyword.
    (r':' + SYMBOL_PATTERN + '?', 'KEYWORD',),

    # Symbols
    (SYMBOL_PATTERN, 'SYMBOL',),

    # Whitespace
    #
    # Note that the whitespace token will contain at most one newline
    (r'[^\S\n\r]*(\n\r?)?', 'WHITESPACE',),

    # Comment
    (r';(([^\n\r]*)(\n\r?)?)', 'COMMENT',),

    # Strings
    (r'"(?P<body>(?:[^\"]|\.)*)"', 'STRING')
]
