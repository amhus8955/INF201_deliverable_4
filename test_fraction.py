"""Tests for the Fraction class."""
import pytest

from fraction import Fraction


def test_init_stores_values():
    f = Fraction(3, 4)
    assert f.numerator == 3
    assert f.denominator == 4


def test_init_default_denominator():
    assert Fraction(5) == Fraction(5, 1)


def test_init_reduces_to_lowest_terms():
    f = Fraction(2, 4)
    assert (f.numerator, f.denominator) == (1, 2)


def test_init_negative_numerator():
    assert Fraction(-1, 2).numerator == -1


@pytest.mark.parametrize("denominator", [0, -1])
def test_init_invalid_denominator(denominator):
    with pytest.raises(ValueError):
        Fraction(1, denominator)


@pytest.mark.parametrize("numerator, denominator", [(1.5, 2), (1, 2.5), ("1", 2)])
def test_init_non_integer(numerator, denominator):
    with pytest.raises(TypeError):
        Fraction(numerator, denominator)


def test_numerator_is_read_only():
    with pytest.raises(AttributeError):
        Fraction(1, 2).numerator = 3


def test_repr_and_str():
    f = Fraction(1, 2)
    assert repr(f) == "Fraction(1, 2)"
    assert str(f) == "1/2"


def test_equal():
    assert Fraction(1, 2) == Fraction(2, 4)
    assert not Fraction(1, 2) == Fraction(1, 3)


def test_not_equal():
    assert Fraction(1, 2) != Fraction(1, 3)
    assert not Fraction(1, 2) != Fraction(2, 4)


def test_less_than():
    assert Fraction(1, 3) < Fraction(1, 2)
    assert not Fraction(1, 2) < Fraction(1, 2)


def test_less_than_or_equal():
    assert Fraction(1, 2) <= Fraction(1, 2)
    assert Fraction(1, 3) <= Fraction(1, 2)
    assert not Fraction(2, 3) <= Fraction(1, 2)


def test_greater_than():
    assert Fraction(2, 3) > Fraction(1, 2)
    assert not Fraction(1, 2) > Fraction(1, 2)


def test_greater_than_or_equal():
    assert Fraction(1, 2) >= Fraction(1, 2)
    assert Fraction(2, 3) >= Fraction(1, 2)
    assert not Fraction(1, 3) >= Fraction(1, 2)


def test_compare_negative_fractions():
    assert Fraction(-1, 2) < Fraction(1, 3)
    assert Fraction(-1, 2) < Fraction(-1, 3)


def test_compare_with_other_type():
    assert Fraction(1, 2) != 0.5
    with pytest.raises(TypeError):
        Fraction(1, 2) < 0.5


def test_add():
    assert Fraction(1, 2) + Fraction(1, 3) == Fraction(5, 6)


def test_sub():
    assert Fraction(1, 2) - Fraction(1, 3) == Fraction(1, 6)
    assert Fraction(1, 3) - Fraction(1, 2) == Fraction(-1, 6)


def test_mul():
    assert Fraction(2, 3) * Fraction(3, 4) == Fraction(1, 2)


def test_truediv():
    assert Fraction(1, 2) / Fraction(1, 4) == Fraction(2, 1)
    assert Fraction(1, 2) / Fraction(-1, 4) == Fraction(-2, 1)


def test_truediv_by_zero():
    with pytest.raises(ZeroDivisionError):
        Fraction(1, 2) / Fraction(0, 5)


def test_arithmetic_with_other_type():
    with pytest.raises(TypeError):
        Fraction(1, 2) + 1



