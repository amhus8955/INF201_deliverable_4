"""
A temperature class supporting Celsius, Fahrenheit and Kelvin.

The :class:`Temperature` class stores a value together with its unit,
converts between the three scales and supports comparisons across
different units, e.g. ``Temperature(0, "C") == Temperature(32, "F")``.
"""

from __future__ import annotations

import math


KELVIN_OFFSET: float = 273.15
"""Difference between the Kelvin and Celsius scales."""

TOLERANCE: float = 1e-9
"""Absolute tolerance (in kelvin) used for floating-point comparisons."""

VALID_UNITS: tuple[str, ...] = ("C", "F", "K")
"""Supported units: Celsius, Fahrenheit and Kelvin."""


class Temperature:
    """A temperature value with a unit of Celsius, Fahrenheit or Kelvin.

    Instances are immutable: ``value`` and ``unit`` are read-only.
    Two temperatures are considered equal if they differ by at most
    ``TOLERANCE`` kelvin, regardless of which units they are stored in.

    Because equality uses a tolerance, instances are not hashable and
    cannot be used as dictionary keys or set members.

    Attributes:
        value: The numeric temperature value, stored as a float.
        unit: The unit of the value, one of ``"C"``, ``"F"`` or ``"K"``.

    Examples:
        >>> Temperature(0, "c") == Temperature(32, "F")
        True
        >>> print(Temperature(100, "C").convert_to("k"))
        373.15 K
    """

    # __slots__ stops new attributes from being added by mistake
    # (e.g. temp.valeu = 5 with a typo raises an error instead).
    __slots__ = ("_value", "_unit")

    def __init__(self, value: float, unit: str = "C") -> None:
        """Create a new temperature.

        Args:
            value: The temperature value.
            unit: The unit of ``value``: ``"C"``, ``"F"`` or ``"K"``
                (case-insensitive). Defaults to ``"C"``.

        Raises:
            ValueError: If the unit is invalid, if the value is not a
                finite number, or if the temperature is below absolute
                zero (0 K).
        """
        # The unit is checked first, because to_kelvin() below needs a
        # valid unit to know which formula to use.
        self._unit: str = self._validate_unit(unit)
        # float() so Temperature(25) and Temperature(25.0) are stored
        # the same way.
        self._value: float = float(value)

        # NaN is never smaller than anything, so it would slip past the
        # absolute zero check below. Infinity is not a real temperature.
        if not math.isfinite(self._value):
            raise ValueError(
                f"Temperature value must be a finite number, got {value!r}."
            )
        # Checked in kelvin, since 0 K is absolute zero in every unit.
        # -TOLERANCE instead of 0, so a tiny rounding error just below
        # 0 K (e.g. after a conversion) does not reject absolute zero.
        if self.to_kelvin() < -TOLERANCE:
            raise ValueError(
                f"{self._value} {self._unit} is below absolute zero (0 K)."
            )

    
    # Read-only attributes:
    # A property without a setter is read-only, so temp.value = 5
    # raises an AttributeError. The data is kept in _value and _unit.
    @property
    def value(self) -> float:
        """float: The numeric temperature value (read-only)."""
        return self._value

    @property
    def unit(self) -> str:
        """str: The unit of the value, ``"C"``, ``"F"`` or ``"K"``."""
        return self._unit

    
    # Helpers:
    # staticmethod because it only needs the unit, not self. It is used
    # by both __init__ and convert_to, so the check is written once.
    @staticmethod
    def _validate_unit(unit: object) -> str:
        """Normalise a unit string and check that it is supported.

        Args:
            unit: The unit to validate, e.g. ``"c"`` or ``"K"``.

        Returns:
            The unit in upper case.

        Raises:
            ValueError: If ``unit`` is not one of ``"C"``, ``"F"`` or
                ``"K"`` (case-insensitive).
        """
        # isinstance is checked first, so e.g. None gives a ValueError
        # instead of an AttributeError from None.upper().
        if not isinstance(unit, str) or unit.upper() not in VALID_UNITS:
            raise ValueError(
                f"Invalid unit {unit!r}. Expected one of {VALID_UNITS}."
            )
        # upper() makes the unit case-insensitive: "c" is stored as "C".
        return unit.upper()

    # Conversions:
    def to_celsius(self) -> float:
        """Return the temperature in degrees Celsius.

        Returns:
            The temperature value converted to Celsius.
        """
        if self._unit == "K":
            return self._value - KELVIN_OFFSET
        if self._unit == "F":
            return (self._value - 32) * 5 / 9
        # Already in Celsius, so no conversion is needed.
        return self._value

    def to_fahrenheit(self) -> float:
        """Return the temperature in degrees Fahrenheit.

        Returns:
            The temperature value converted to Fahrenheit.
        """
        if self._unit == "C":
            return self._value * 9 / 5 + 32
        if self._unit == "K":
            return (self._value - KELVIN_OFFSET) * 9 / 5 + 32
        return self._value

    def to_kelvin(self) -> float:
        """Return the temperature in kelvin.

        Returns:
            The temperature value converted to Kelvin.
        """
        if self._unit == "C":
            return self._value + KELVIN_OFFSET
        if self._unit == "F":
            return (self._value - 32) * 5 / 9 + KELVIN_OFFSET
        return self._value

    def convert_to(self, target_unit: str) -> Temperature:
        """Return a new temperature converted to ``target_unit``.

        The original instance is not changed.

        Args:
            target_unit: The unit to convert to: ``"C"``, ``"F"`` or
                ``"K"`` (case-insensitive).

        Returns:
            A new :class:`Temperature` instance in the target unit.

        Raises:
            ValueError: If ``target_unit`` is not a valid unit.
        """
        target = self._validate_unit(target_unit)
        # The dictionary links each unit to the method that converts to
        # it, instead of a long if/elif chain. The methods are stored
        # without () and called on the last line.
        converters = {
            "C": self.to_celsius,
            "F": self.to_fahrenheit,
            "K": self.to_kelvin,
        }
        # A new object is returned, because self is read-only.
        return Temperature(converters[target](), target)

    # String representations:
    def __repr__(self) -> str:
        """Return an unambiguous representation of the temperature.

        Returns:
            A string such as ``"Temperature(25.0, 'C')"``.
        """
        # !r adds quotes around the unit, so the string looks like the
        # code that creates the object: Temperature(25.0, 'C').
        return f"{type(self).__name__}({self._value!r}, {self._unit!r})"

    def __str__(self) -> str:
        """Return a human-readable string with two decimals.

        Kelvin is an absolute scale and is written without a degree
        sign, following SI conventions.

        Returns:
            A string such as ``"25.00 °C"``, ``"77.00 °F"`` or
            ``"298.15 K"``.
        """
        symbol = "K" if self._unit == "K" else f"°{self._unit}"
        # :.2f rounds the value to two decimals, e.g. 36.666 -> 36.67.
        return f"{self._value:.2f} {symbol}"

    
    # Comparisons (done in kelvin, using TOLERANCE):
    # Both temperatures are converted to kelvin before comparing, so
    # it does not matter which units they are stored in.
    def _is_close(self, other: Temperature) -> bool:
        """Check whether two temperatures are equal within the tolerance.

        Args:
            other: The temperature to compare with.

        Returns:
            True if the temperatures differ by at most ``TOLERANCE``
            kelvin, otherwise False.
        """
        # Floats are not exact (0.1 + 0.2 != 0.3 in Python), so == on
        # floats can fail even when the temperatures are the same.
        return abs(self.to_kelvin() - other.to_kelvin()) <= TOLERANCE

    def __eq__(self, other: object) -> bool:
        """Return True if both temperatures are equal within tolerance.

        Args:
            other: The object to compare with.

        Returns:
            Whether the temperatures are equal, or ``NotImplemented``
            if ``other`` is not a :class:`Temperature`.
        """
        # NotImplemented (not False) tells Python that we do not know
        # how to compare with this type, so Python can try the other
        # object's method instead.
        if not isinstance(other, Temperature):
            return NotImplemented
        return self._is_close(other)

    def __ne__(self, other: object) -> bool:
        """Return True if the temperatures are not equal within tolerance.

        Args:
            other: The object to compare with.

        Returns:
            Whether the temperatures differ, or ``NotImplemented`` if
            ``other`` is not a :class:`Temperature`.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        return not self._is_close(other)

    def __lt__(self, other: object) -> bool:
        """Return True if this temperature is lower than other.

        Args:
            other: The object to compare with.

        Returns:
            Whether ``self < other``, or ``NotImplemented`` if
            ``other`` is not a :class:`Temperature`.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        # Equal within the tolerance means "not lower", even if the
        # floats differ by a tiny rounding error.
        if self._is_close(other):
            return False
        return self.to_kelvin() < other.to_kelvin()

    def __le__(self, other: object) -> bool:
        """Return True if this temperature is lower than or equal to other.

        Args:
            other: The object to compare with.

        Returns:
            Whether ``self <= other``, or ``NotImplemented`` if
            ``other`` is not a :class:`Temperature`.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        # Equal within the tolerance counts as "lower or equal".
        if self._is_close(other):
            return True
        return self.to_kelvin() < other.to_kelvin()

    def __gt__(self, other: object) -> bool:
        """Return True if this temperature is higher than other.

        Args:
            other: The object to compare with.

        Returns:
            Whether ``self > other``, or ``NotImplemented`` if
            ``other`` is not a :class:`Temperature`.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        if self._is_close(other):
            return False
        return self.to_kelvin() > other.to_kelvin()

    def __ge__(self, other: object) -> bool:
        """Return True if this temperature is higher than or equal to other.

        Args:
            other: The object to compare with.

        Returns:
            Whether ``self >= other``, or ``NotImplemented`` if
            ``other`` is not a :class:`Temperature`.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        if self._is_close(other):
            return True
        return self.to_kelvin() > other.to_kelvin()
