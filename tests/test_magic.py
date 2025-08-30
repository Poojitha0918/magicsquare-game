import pytest
from magic import siamese, magic_constant, is_valid_solution

@pytest.mark.parametrize("n", [3,5,7,9])
def test_siamese_valid(n):
    sq = siamese(n)
    assert len(sq) == n and all(len(row) == n for row in sq)
    assert is_valid_solution(sq)
    # Check magic constant
    target = magic_constant(n)
    assert sum(sq[0]) == target
