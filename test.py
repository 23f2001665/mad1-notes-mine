import pytest

@pytest.mark.parametrize("x,y, expected", [
    (1, 2, 3),
    (2, 3, 5),
    (3, 3, 7)
])
def test_addition(x, y, expected):
    assert x + y == expected

def test_subtraction():
    assert 5 - 2 == 3
    assert 10 - 5 == 5
    assert 7 - 3 == 4