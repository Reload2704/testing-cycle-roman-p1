import pytest

from roman.converter import RomanError, from_roman, is_valid_roman, add_roman


# ---------------------------------------------------------------------------
# AC1 - Section 3: leading and trailing whitespace is tolerated.
# ---------------------------------------------------------------------------

def test_ac1_input_from_a_user_facing_field_is_trimmed():
    assert from_roman("  IV  ") == 4
    assert from_roman("X ") == 10
    assert is_valid_roman("  IV  ") is True

    with pytest.raises(RomanError):
        from_roman("X I")


# ---------------------------------------------------------------------------
# AC2 - Sections 4 and 6: only the canonical form is accepted.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", ["IIII", "VIIII", "XXXX", "VV"])
def test_ac2_non_canonical_numerals_are_rejected(text):
    with pytest.raises(RomanError):
        from_roman(text)

    assert is_valid_roman(text) is False


def test_ac2_canonical_numerals_are_still_accepted():
    assert from_roman("IV") == 4
    assert from_roman("MCMXCIV") == 1994
    assert is_valid_roman("IV") is True


# ---------------------------------------------------------------------------
# AC3 - Section 7: roman arithmetic returns a canonical numeral in range.
# ---------------------------------------------------------------------------

def test_ac3_roman_arithmetic_returns_the_canonical_numeral():
    assert add_roman("II", "II") == "IV"


def test_ac3_roman_arithmetic_rejects_a_result_out_of_range():
    with pytest.raises(RomanError):
        add_roman("MMM", "M")
