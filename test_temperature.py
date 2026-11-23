"""
Pytest tests for the :class:`Temperature` class in ``temperature.py``.

Run with::

    pytest -v test_temperature.py
"""

import pytest

from temperature import Temperature

# Converted floats are rarely exact, so they are checked with
# pytest.approx and the same tolerance as in the class.
TOL: float = 1e-9
"""Absolute tolerance used when checking converted float values."""

# Reference points as (celsius, fahrenheit, kelvin). pytest.param with
# an id gives readable test names in the output, e.g. "water_boils".
REFERENCE_POINTS = [
    pytest.param(-273.15, -459.67, 0.0, id="absolute_zero"),
    pytest.param(-40.0, -40.0, 233.15, id="celsius_fahrenheit_crossover"),
    pytest.param(0.0, 32.0, 273.15, id="water_freezes"),
    pytest.param(37.0, 98.6, 310.15, id="body_temperature"),
    pytest.param(100.0, 212.0, 373.15, id="water_boils"),
]

UNITS: list[str] = ["C", "F", "K"]



# 1. Initialisation:
def test_default_unit_is_celsius() -> None:
    """A temperature created without a unit should be in Celsius."""
    temp = Temperature(20)
    assert temp.unit == "C"
    assert temp.value == 20.0


# parametrize runs the same test once for each value, so the test does
# not have to be copied six times.
@pytest.mark.parametrize("unit", ["c", "C", "f", "F", "k", "K"])
def test_unit_is_case_insensitive(unit: str) -> None:
    """Units should be accepted in any case and stored in upper case."""
    assert Temperature(300, unit).unit == unit.upper()


def test_value_is_stored_as_float() -> None:
    """An integer value should be stored as a float."""
    temp = Temperature(25, "C")
    assert isinstance(temp.value, float)
    assert temp.value == 25.0


def test_value_is_read_only() -> None:
    """Assigning to ``value`` should raise an AttributeError."""
    temp = Temperature(25, "C")
    # pytest.raises makes the test fail if the error does NOT happen.
    # "type: ignore" tells mypy that the wrong assignment is on purpose.
    with pytest.raises(AttributeError):
        temp.value = 30  # type: ignore[misc]
    # The value must also be unchanged after the failed assignment.
    assert temp.value == 25.0


def test_unit_is_read_only() -> None:
    """Assigning to ``unit`` should raise an AttributeError."""
    temp = Temperature(25, "C")
    with pytest.raises(AttributeError):
        temp.unit = "F"  # type: ignore[misc]
    assert temp.unit == "C"



# 2. Validation:
# Includes edge cases: an empty string, a full word, a unit with a
# space in front, and values that are not strings at all.
@pytest.mark.parametrize("unit", ["X", "", "Celsius", "CF", " C", None, 1])
def test_invalid_unit_raises_value_error(unit: object) -> None:
    """Units other than C, F and K should raise a ValueError."""
    # match checks the error message, so we know it is the right error.
    with pytest.raises(ValueError, match="Invalid unit"):
        Temperature(0, unit)  # type: ignore[arg-type]

# Each value is just below absolute zero in its own unit.
@pytest.mark.parametrize(
    "value, unit",
    [(-273.16, "C"), (-459.68, "F"), (-0.01, "K"), (-1000, "c")],
)
def test_below_absolute_zero_raises_value_error(
    value: float, unit: str
) -> None:
    """Temperatures below 0 K should raise a ValueError in every unit."""
    with pytest.raises(ValueError, match="below absolute zero"):
        Temperature(value, unit)


# Edge case: exactly 0 K is allowed, only values below it are invalid.
@pytest.mark.parametrize(
    "value, unit", [(-273.15, "C"), (-459.67, "F"), (0, "K")]
)
def test_exactly_absolute_zero_is_allowed(value: float, unit: str) -> None:
    """Exactly absolute zero is a valid temperature in every unit."""
    assert Temperature(value, unit).to_kelvin() == pytest.approx(0, abs=TOL)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_non_finite_value_raises_value_error(value: float) -> None:
    """NaN and infinity are not valid temperatures."""
    with pytest.raises(ValueError, match="finite"):
        Temperature(value, "C")

@pytest.mark.parametrize("target_unit", ["X", "", "kelvin", None])
def test_convert_to_invalid_unit_raises_value_error(
    target_unit: object,
) -> None:
    """``convert_to`` should raise a ValueError for an invalid unit."""
    with pytest.raises(ValueError, match="Invalid unit"):
        Temperature(0, "C").convert_to(target_unit)  # type: ignore[arg-type]


# 3. Conversions
# Two parametrize decorators give every combination:
# 3 start units x 5 reference points = 15 tests.
@pytest.mark.parametrize("celsius, fahrenheit, kelvin", REFERENCE_POINTS)
@pytest.mark.parametrize("source_unit", UNITS)
def test_conversion_methods(
    source_unit: str, celsius: float, fahrenheit: float, kelvin: float
) -> None:
    """``to_celsius``, ``to_fahrenheit`` and ``to_kelvin`` are accurate."""
    # Picks the start value that matches the start unit.
    values = {"C": celsius, "F": fahrenheit, "K": kelvin}
    temp = Temperature(values[source_unit], source_unit)

    assert temp.to_celsius() == pytest.approx(celsius, abs=TOL)
    assert temp.to_fahrenheit() == pytest.approx(fahrenheit, abs=TOL)
    assert temp.to_kelvin() == pytest.approx(kelvin, abs=TOL)
