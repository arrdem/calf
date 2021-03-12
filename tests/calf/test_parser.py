"""
Tests of calf.parser
"""


import calf.parser as cp

import pytest


@pytest.mark.parametrize('text, element_types', [
    # Integers
    ("(1)", ["INTEGER"]),
    ("( 1 )", ["INTEGER"]),
    ("(,1,)", ["INTEGER"]),
    ("(1\n)", ["INTEGER"]),
    ("(\n1\n)", ["INTEGER"]),
    ("(1, 2, 3, 4)", ["INTEGER", "INTEGER", "INTEGER", "INTEGER"]),

    # Floats
    ("(1.0)", ["FLOAT"]),
    ("(1.0e0)", ["FLOAT"]),
    ("(1e0)", ["FLOAT"]),
    ("(1e0)", ["FLOAT"]),

    # Symbols
    ("(foo)", ["SYMBOL"]),
    ("(+)", ["SYMBOL"]),
    ("(-)", ["SYMBOL"]),
    ("(*)", ["SYMBOL"]),
    ("(foo-bar)", ["SYMBOL"]),
    ("(+foo-bar+)", ["SYMBOL"]),
    ("(+foo-bar+)", ["SYMBOL"]),
    ("( foo bar )", ["SYMBOL", "SYMBOL"]),

    # Keywords
    ("(:foo)", ["KEYWORD"]),
    ("( :foo )", ["KEYWORD"]),
    ("(\n:foo\n)", ["KEYWORD"]),
    ("(,:foo,)", ["KEYWORD"]),
    ("(:foo :bar)", ["KEYWORD", "KEYWORD"]),
    ("(:foo :bar 1)", ["KEYWORD", "KEYWORD", "INTEGER"]),
])
def test_parse_list(text, element_types):
    """Test we can parse various lists of contents."""
    l_t = next(cp.parse_buffer(text, discard_whitespace=True))
    assert l_t.type == "LIST"
    assert [t.type for t in l_t] == element_types


@pytest.mark.parametrize('text, element_types', [
    # Integers
    ("[1]", ["INTEGER"]),
    ("[ 1 ]", ["INTEGER"]),
    ("[,1,]", ["INTEGER"]),
    ("[1\n]", ["INTEGER"]),
    ("[\n1\n]", ["INTEGER"]),
    ("[1, 2, 3, 4]", ["INTEGER", "INTEGER", "INTEGER", "INTEGER"]),

    # Floats
    ("[1.0]", ["FLOAT"]),
    ("[1.0e0]", ["FLOAT"]),
    ("[1e0]", ["FLOAT"]),
    ("[1e0]", ["FLOAT"]),

    # Symbols
    ("[foo]", ["SYMBOL"]),
    ("[+]", ["SYMBOL"]),
    ("[-]", ["SYMBOL"]),
    ("[*]", ["SYMBOL"]),
    ("[foo-bar]", ["SYMBOL"]),
    ("[+foo-bar+]", ["SYMBOL"]),
    ("[+foo-bar+]", ["SYMBOL"]),
    ("[ foo bar ]", ["SYMBOL", "SYMBOL"]),

    # Keywords
    ("[:foo]", ["KEYWORD"]),
    ("[ :foo ]", ["KEYWORD"]),
    ("[\n:foo\n]", ["KEYWORD"]),
    ("[,:foo,]", ["KEYWORD"]),
    ("[:foo :bar]", ["KEYWORD", "KEYWORD"]),
    ("[:foo :bar 1]", ["KEYWORD", "KEYWORD", "INTEGER"]),
])
def test_parse_sqlist(text, element_types):
    """Test we can parse various 'square' lists of contents."""
    l_t = next(cp.parse_buffer(text, discard_whitespace=True))
    assert l_t.type == "SQLIST"
    assert [t.type for t in l_t] == element_types


@pytest.mark.parametrize('text, element_pairs', [
])
def test_parse_dict(text, element_pairs):
    """Test we can parse various mappings."""
