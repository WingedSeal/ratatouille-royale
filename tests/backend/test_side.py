import pytest

from ratroyale.backend.side import Side


@pytest.mark.parametrize("value", range(len(Side) + 1))
def test_side_int(value: int) -> None:
    assert Side.to_int(Side.from_int(value)) == value


def test_other_side() -> None:
    assert Side.MOUSE.other_side() == Side.RAT
    assert Side.RAT.other_side() == Side.MOUSE
