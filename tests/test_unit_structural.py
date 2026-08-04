import pytest

from roman.converter import (
    RomanError,
    to_roman,
    from_roman,
    is_valid_roman,
    add_roman,
    subtract_roman,
    _roundtrip_differs,
    _count_char,
)


# ---------------------------------------------------------------------------
# 3.11  Basis set of to_roman.
# ---------------------------------------------------------------------------

def test_p2_non_integer_is_rejected():
    """src,40,41a,42,snk - 41a true."""
    with pytest.raises(RomanError):
        to_roman("X")


def test_p3_bool_is_rejected():
    """src,40,41a,41b,42,snk - 41a false, 41b true (True is not 1)."""
    with pytest.raises(RomanError):
        to_roman(True)


def test_p4_below_minimum_is_rejected():
    """src,40,41a,41b,43,44,snk - guard n < 1."""
    with pytest.raises(RomanError):
        to_roman(0)


def test_p5_above_maximum_is_rejected():
    """src,40,41a,41b,43,45,46,snk - guard n > 3999."""
    with pytest.raises(RomanError):
        to_roman(4000)


def test_p7_loop_body_executes_once():
    """src,...,49,50,51,52,50,49,53,snk - the only feasible path through 51-52."""
    assert to_roman(1) == "I"


# ---------------------------------------------------------------------------
# 3.11  Boundaries of the guards at 43 and 45 (on-point / off-point).
# ---------------------------------------------------------------------------

def test_lower_boundary_is_accepted():
    assert to_roman(1) == "I"


def test_upper_boundary_is_accepted():
    assert to_roman(3999) == "MMMCMXCIX"


def test_negative_is_rejected():
    with pytest.raises(RomanError):
        to_roman(-1)


def test_float_is_rejected():
    with pytest.raises(RomanError):
        to_roman(4.0)


# ---------------------------------------------------------------------------
# 3.12  Definition-use pairs of `remaining` created inside the loop.
#       (48,50) p-use, (48,52) c-use, (52,50) p-use, (52,52) c-use.
# ---------------------------------------------------------------------------

def test_du_remaining_single_subtraction():
    """(48,52) then (52,50): remaining is defined at 48, used at 52, and the
    value redefined at 52 is re-tested by the predicate at 50."""
    assert to_roman(2) == "II"


def test_du_remaining_repeated_subtraction():
    """(52,52): the value redefined at 52 is used again at 52 on the next
    iteration of the inner while."""
    assert to_roman(3) == "III"


def test_du_remaining_across_pairs():
    """(52,50) across two different iterations of the outer for: remaining is
    carried from one (value, symbol) pair to the next."""
    assert to_roman(1666) == "MDCLXVI"


def test_du_out_accumulates():
    """out is defined at 47, redefined by append at 51, and c-used at 53."""
    assert to_roman(2000) == "MM"


# ---------------------------------------------------------------------------
# 3.13  Coverage of the remaining branches of converter.py.
#       from_roman: lines 58, 61, 64, 72-74, 79, 83.
# ---------------------------------------------------------------------------

def test_from_roman_non_string_is_rejected():
    """line 58."""
    with pytest.raises(RomanError):
        from_roman(5)


def test_from_roman_empty_is_rejected():
    """line 61."""
    with pytest.raises(RomanError):
        from_roman("")


def test_from_roman_unknown_character_is_rejected():
    """line 64."""
    with pytest.raises(RomanError):
        from_roman("Z")


def test_from_roman_valid_subtractive_pair():
    """lines 72-74, the subtractive branch."""
    assert from_roman("IV") == 4
    assert from_roman("MCMXCIV") == 1994


def test_from_roman_invalid_subtractive_pair_is_rejected():
    """line 79."""
    with pytest.raises(RomanError):
        from_roman("IL")


def test_from_roman_out_of_range_is_rejected():
    """line 83."""
    with pytest.raises(RomanError):
        from_roman("MMMM")


# ---------------------------------------------------------------------------
# 3.13  is_valid_roman: lines 100-104.
# ---------------------------------------------------------------------------

def test_is_valid_roman_accepts_canonical():
    assert is_valid_roman("IV") is True


def test_is_valid_roman_rejects_unknown_symbol():
    assert is_valid_roman("Z") is False


def test_is_valid_roman_never_raises_on_wrong_type():
    assert is_valid_roman(123) is False
    assert is_valid_roman(None) is False


# ---------------------------------------------------------------------------
# 3.13  add_roman / subtract_roman: lines 108 and 112.
#       Only for line coverage here; the collaboration between the units is
#       tested in Part 4.
# ---------------------------------------------------------------------------

def test_add_roman_reaches_line_108():
    assert add_roman("IV", "VI") == "X"


def test_subtract_roman_reaches_line_112():
    assert subtract_roman("X", "I") == "IX"


# ---------------------------------------------------------------------------
# 3.13  Private helpers, unreachable from the public API (lines 88 and 92-96).
# ---------------------------------------------------------------------------

def test_roundtrip_differs_helper():
    """line 88."""
    assert _roundtrip_differs(1, "II") is True
    assert _roundtrip_differs(1, "I") is False


def test_count_char_helper():
    """lines 92-96, both outcomes of the predicate at 94."""
    assert _count_char("XXI", "X") == 2
    assert _count_char("XXI", "M") == 0


# ---------------------------------------------------------------------------
# Defects revealed at the unit level.  _PAIRS holds (5, "IV") where the
# specification requires (4, "IV"), so 4 is never emitted subtractively.
# These are fixed in Part 6; they are left failing on purpose here.
# ---------------------------------------------------------------------------

def test_four_is_canonical():
    assert to_roman(4) == "IV"


def test_fourteen_is_canonical():
    assert to_roman(14) == "XIV"


def test_1994_is_canonical():
    assert to_roman(1994) == "MCMXCIV"


def test_never_four_identical_symbols_in_a_row():
    for n in range(1, 4000):
        assert "IIII" not in to_roman(n)
