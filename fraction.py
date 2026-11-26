"""A class for fractions."""
from __future__ import annotations

from math import gcd


class Fraction:
    """A fraction with an integer numerator and a strictly positive integer denominator."""

    def __init__(self, numerator: int, denominator: int = 1) -> None:
        """
        Create a fraction and reduce it to lowest terms.

        Args:
            numerator (int): The numerator.
            denominator (int): The denominator, must be greater than 0 (default = 1).

        Raises:
            TypeError: If numerator or denominator is not an integer.
            ValueError: If denominator is not greater than 0.
        """
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise TypeError("Numerator and denominator must be integers")
        if denominator <= 0:
            raise ValueError("Denominator must be greater than 0")
        divisor = gcd(numerator, denominator)
        self._numerator = numerator // divisor
        self._denominator = denominator // divisor

    @property
    def numerator(self) -> int:
        """Read-only numerator."""
        return self._numerator

    @property
    def denominator(self) -> int:
        """Read-only denominator."""
        return self._denominator

    def __repr__(self) -> str:
        """Unambiguous representation, e.g. Fraction(1, 2)."""
        return f"Fraction({self.numerator}, {self.denominator})"

    def __str__(self) -> str:
        """Readable representation, e.g. 1/2."""
        return f"{self.numerator}/{self.denominator}"

    def __eq__(self, other: object) -> bool:
        """Equal to another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return self.numerator * other.denominator == other.numerator * self.denominator

    def __ne__(self, other: object) -> bool:
        """Not equal to another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return not self == other

    def __lt__(self, other: Fraction) -> bool:
        """Smaller than another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return self.numerator * other.denominator < other.numerator * self.denominator

    def __le__(self, other: Fraction) -> bool:
        """Smaller than or equal to another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return self.numerator * other.denominator <= other.numerator * self.denominator

    def __gt__(self, other: Fraction) -> bool:
        """Greater than another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return self.numerator * other.denominator > other.numerator * self.denominator

    def __ge__(self, other: Fraction) -> bool:
        """Greater than or equal to another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return self.numerator * other.denominator >= other.numerator * self.denominator

    def __add__(self, other: Fraction) -> Fraction:
        """Add two fractions."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return Fraction(self.numerator * other.denominator + other.numerator * self.denominator,
                        self.denominator * other.denominator)

    def __sub__(self, other: Fraction) -> Fraction:
        """Subtract another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return Fraction(self.numerator * other.denominator - other.numerator * self.denominator,
                        self.denominator * other.denominator)

    def __mul__(self, other: Fraction) -> Fraction:
        """Multiply two fractions."""
        if not isinstance(other, Fraction):
            return NotImplemented
        return Fraction(self.numerator * other.numerator, self.denominator * other.denominator)

    def __truediv__(self, other: Fraction) -> Fraction:
        """Divide by another fraction."""
        if not isinstance(other, Fraction):
            return NotImplemented
        if other.numerator == 0:
            raise ZeroDivisionError("Cannot divide by a fraction equal to 0")
        sign = 1 if other.numerator > 0 else -1
        return Fraction(sign * self.numerator * other.denominator, abs(other.numerator) * self.denominator)














    