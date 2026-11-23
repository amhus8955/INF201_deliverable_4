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

@pytest.mark.parametrize("celsius, fahrenheit, kelvin", REFERENCE_POINTS)
@pytest.mark.parametrize("target_unit", UNITS)
def test_convert_to_returns_new_temperature(
    target_unit: str, celsius: float, fahrenheit: float, kelvin: float
) -> None:
    """``convert_to`` returns a new instance and leaves the original."""
    values = {"C": celsius, "F": fahrenheit, "K": kelvin}
    original = Temperature(celsius, "C")

    # lower() also checks that convert_to is case-insensitive.
    converted = original.convert_to(target_unit.lower())

    assert isinstance(converted, Temperature)
    # "is not" checks that it is a new object, not the same one.
    assert converted is not original
    assert converted.unit == target_unit
    assert converted.value == pytest.approx(values[target_unit], abs=TOL)
    assert original.value == celsius
    assert original.unit == "C"


# 4. Round-trip conversions
# 21.5 and 1234.5678 check "uneven" numbers, not only reference points.
@pytest.mark.parametrize(
    "celsius", [-273.15, -40.0, 0.0, 21.5, 37.0, 100.0, 1234.5678]
)
def test_round_trip_c_f_k_c(celsius: float) -> None:
    """Converting C -> F -> K -> C reproduces the original temperature."""
    original = Temperature(celsius, "C")

    # Each convert_to returns a new Temperature, so the calls can be
    # chained.
    result = original.convert_to("F").convert_to("K").convert_to("C")

    assert result == original
    assert result.unit == "C"
    assert result.value == pytest.approx(celsius, abs=TOL)


# 5. Cross-unit comparisons
@pytest.mark.parametrize("celsius, fahrenheit, kelvin", REFERENCE_POINTS)
def test_equality_across_units(
    celsius: float, fahrenheit: float, kelvin: float
) -> None:
    """The same temperature in different units should compare equal."""
    temp_c = Temperature(celsius, "C")
    temp_f = Temperature(fahrenheit, "F")
    temp_k = Temperature(kelvin, "K")

    assert temp_c == temp_f == temp_k
    assert not temp_c != temp_f
    assert not temp_f != temp_k


def test_inequality_across_units() -> None:
    """Different temperatures should not compare equal."""
    assert Temperature(0, "C") != Temperature(33, "F")
    assert not Temperature(0, "C") == Temperature(274, "K")


def test_equality_uses_tolerance() -> None:
    """Differences within 1e-9 are equal, larger differences are not."""
    base = Temperature(0, "C")
    # 1e-10 is inside the tolerance of 1e-9, while 1e-8 is outside it.
    assert base == Temperature(1e-10, "C")
    assert base != Temperature(1e-8, "C")


def test_ordering_across_units() -> None:
    """``<``, ``<=``, ``>`` and ``>=`` should work across mixed units."""
    cold = Temperature(0, "C")  # 273.15 K
    warm = Temperature(98.6, "F")  # 310.15 K
    hot = Temperature(373.15, "K")  # 100 degrees Celsius

    assert cold < warm < hot
    assert hot > warm > cold
    assert cold <= warm <= hot
    assert hot >= warm >= cold
    assert not warm < cold
    assert not cold > warm


@pytest.mark.parametrize("celsius, fahrenheit, kelvin", REFERENCE_POINTS)
def test_ordering_with_equal_temperatures(
    celsius: float, fahrenheit: float, kelvin: float
) -> None:
    """Equal temperatures in different units: ``<=``/``>=`` but not ``<``."""
    temp_c = Temperature(celsius, "C")
    temp_f = Temperature(fahrenheit, "F")
    temp_k = Temperature(kelvin, "K")

    # Equal temperatures must count as <= and >=, but never < or >.
    assert temp_c <= temp_f and temp_c >= temp_f
    assert temp_f <= temp_k and temp_f >= temp_k
    assert not temp_c < temp_f and not temp_c > temp_f
    assert not temp_f < temp_k and not temp_f > temp_k


def test_sorting_mixed_units() -> None:
    """A list of temperatures in mixed units can be sorted."""
    temps = [
        Temperature(212, "F"),
        Temperature(0, "K"),
        Temperature(20, "C"),
        Temperature(-40, "F"),
    ]
    # sorted() uses < to compare, so this also tests __lt__. The repr
    # strings are compared to check that the units are kept as well.
    assert [repr(t) for t in sorted(temps)] == [
        "Temperature(0.0, 'K')",
        "Temperature(-40.0, 'F')",
        "Temperature(20.0, 'C')",
        "Temperature(212.0, 'F')",
    ]


@pytest.mark.parametrize("other", [0, 273.15, "0 C", None])
def test_comparison_with_non_temperature(other: object) -> None:
    """Comparing with a non-Temperature returns ``NotImplemented``."""
    temp = Temperature(0, "C")

    # The methods are called directly to see the NotImplemented value,
    # since Python hides it when we use the normal operators.
    assert temp.__eq__(other) is NotImplemented
    assert temp.__ne__(other) is NotImplemented
    assert temp.__lt__(other) is NotImplemented
    assert temp.__le__(other) is NotImplemented
    assert temp.__gt__(other) is NotImplemented
    assert temp.__ge__(other) is NotImplemented

    # Python then falls back to identity for == and != ...
    assert (temp == other) is False
    assert (temp != other) is True
    # ... and raises a TypeError for ordering.
    with pytest.raises(TypeError):
        _ = temp < other


# 6. Formatting
# 36.666 checks that str() rounds to two decimals (36.67).
@pytest.mark.parametrize(
    "temp, expected",
    [
        (Temperature(25, "C"), "25.00 °C"),
        (Temperature(98.6, "f"), "98.60 °F"),
        (Temperature(-40, "C"), "-40.00 °C"),
        (Temperature(36.666, "C"), "36.67 °C"),
        (Temperature(298.15, "k"), "298.15 K"),
    ],
    ids=["celsius", "fahrenheit", "negative", "rounding", "kelvin"],
)
def test_str(temp: Temperature, expected: str) -> None:
    """``str()`` gives a human-readable string with two decimals."""
    assert str(temp) == expected


@pytest.mark.parametrize(
    "temp, expected",
    [
        (Temperature(25, "C"), "Temperature(25.0, 'C')"),
        (Temperature(98.6, "f"), "Temperature(98.6, 'F')"),
        (Temperature(0, "K"), "Temperature(0.0, 'K')"),
    ],
    ids=["celsius", "fahrenheit", "kelvin"],
)
def test_repr(temp: Temperature, expected: str) -> None:
    """``repr()`` gives an unambiguous representation."""
    assert repr(temp) == expected


def test_repr_can_recreate_object() -> None:
    """Evaluating ``repr()`` should give back an equal temperature."""
    temp = Temperature(36.6, "C")
    # An unambiguous repr can be run as code to create the same object.
    # eval only gets access to Temperature, and the input is our own.
    recreated = eval(repr(temp), {"Temperature": Temperature})
    assert recreated == temp
    assert recreated.unit == temp.unit
