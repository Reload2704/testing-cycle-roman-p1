import pytest

from roman.converter import (
    RomanError,
    from_roman,
    is_valid_roman,
    add_roman,
    subtract_roman,
)

from tests.spec_oracle import is_canonical


# ---------------------------------------------------------------------------
# Mandatory examples of section 7.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("a,b,expected", [
    ("II", "II", "IV"),
    ("IV", "VI", "X"),
    ("MCMXCIV", "VI", "MM"),
])
def test_add_roman_mandatory_examples(a, b, expected):
    assert add_roman(a, b) == expected


def test_subtract_roman_mandatory_example():
    assert subtract_roman("X", "I") == "IX"


def test_add_roman_above_range_raises():
    with pytest.raises(RomanError):
        add_roman("MMM", "M")


def test_subtract_roman_below_range_raises():
    with pytest.raises(RomanError):
        subtract_roman("I", "I")


def test_subtract_roman_negative_result_raises():
    with pytest.raises(RomanError):
        subtract_roman("I", "X")

@pytest.mark.parametrize("a,b", [
    ("II", "II"), ("IV", "VI"), ("MCMXCIV", "VI"), ("XL", "IX"), ("MM", "MCMXCIX"),
])
def test_add_roman_agrees_with_integer_arithmetic(a, b):
    assert from_roman(add_roman(a, b)) == from_roman(a) + from_roman(b)



@pytest.mark.parametrize("a,b", [("II", "II"), ("X", "IV"), ("MCMXCIII", "I")])
def test_add_roman_result_is_accepted_by_is_valid_roman(a, b):
    assert is_valid_roman(add_roman(a, b)) is True


@pytest.mark.parametrize("a,b", [("II", "II"), ("I", "III"), ("X", "IV"), ("MCMXCIII", "I")])
def test_add_roman_result_is_canonical(a, b):
    result = add_roman(a, b)
    assert is_canonical(result), f"add_roman({a!r}, {b!r}) returned {result!r}"


def test_subtract_roman_result_is_canonical():
    result = subtract_roman("V", "I")
    assert is_canonical(result), f"subtract_roman('V', 'I') returned {result!r}"


def test_the_validator_agrees_with_the_specification():
    """`is_valid_roman` must reject what section 4 rejects. This is the second
    half of the masking: the validator is as permissive as the generator is
    wrong, which is why the test above is needed at all."""
    assert is_canonical("IIII") is False
    assert is_valid_roman("IIII") is False
