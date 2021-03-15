"""
"""

from conftest import parametrize

from calf.reader import read_buffer

@parametrize('text', [
    "()",
    "[]",
    "[[[[[[[[[]]]]]]]]]",
    "{}()[]",
    "[:foo bar 'baz lo/l, 1, 1.2. 1e-5 -1e2]",
    '"foo"',
])
def test_read(text):
    assert list(read_buffer(text))
