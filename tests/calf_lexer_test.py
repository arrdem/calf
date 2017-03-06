"""
Tests of calf.lexer
"""

import calf.lexer as cl
from conftest import parametrize

import pytest


def lex_single_token(buffer):
    """Lexes a single token from the buffer."""
    return cl.lex_buffer(buffer).__iter__().next()


@parametrize('text,token_type', [
    ("(", "PAREN_LEFT",),
    (")", "PAREN_RIGHT",),
    ("[", "BRACKET_LEFT",),
    ("]", "BRACKET_RIGHT",),
    ("{", "BRACE_LEFT",),
    ("}", "BRACE_RIGHT",),
    ("^", "META",),
    ("#", "MACRO_DISPATCH",),

    ("foo", "SYMBOL",),
    ("foo/bar", "SYMBOL"),
    (":foo", 'KEYWORD',),
    (":foo/bar", 'KEYWORD',),
    (" \t\n\r", "WHITESPACE",),
    ("      \n", "WHITESPACE",),
    ("; this is a sample comment\n", "COMMENT")
])
def test_lex_examples(text, token_type):
    t = lex_single_token(text)
    assert t.value == text
    assert t.type == token_type
