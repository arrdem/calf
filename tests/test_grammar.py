"""
Tests covering the Calf grammar.
"""

import re

from calf import grammar as cg
from conftest import parametrize


@parametrize('ex', [
    # Proper strings
    '""',
    '"foo bar"',
    '"foo\n bar\n\r qux"',
    '"foo\\"bar"',

    # Unterminated string cases
    '"',
    '"f',
    '"foo bar',
    '"foo\\" bar',
])
def test_match_string(ex):
    assert re.fullmatch(cg.STRING_PATTERN, ex)


@parametrize('ex', [
    # Proper strings
    '""""""',
    '"""foo bar baz"""',
    '"""foo  "" "" "" bar baz"""',

    # Unterminated string case
    '"""foo bar baz',
])
def test_match_tstring(ex):
    assert re.fullmatch(cg.TRIPPLE_STRING_PATTERN, ex)
