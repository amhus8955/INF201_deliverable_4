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
