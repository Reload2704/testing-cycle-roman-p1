class RomanError(ValueError):
    pass


_PAIRS = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)


_SINGLE = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}


_VALID_SUBTRACTIVE = {"IV", "IX", "XL", "XC", "CD", "CM"}


_MIN_VALUE = 1
_MAX_VALUE = 3999


def to_roman(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise RomanError("value must be an integer")
    if n < _MIN_VALUE:
        raise RomanError("value must be >= 1")
    if n > _MAX_VALUE:
        raise RomanError("value must be <= 3999")
    out = []
    remaining = n
    for value, symbol in _PAIRS:
        while remaining >= value:
            out.append(symbol)
            remaining -= value
    return "".join(out)


def from_roman(s):
    if not isinstance(s, str):
        raise RomanError("value must be a string")
    text = s.strip().upper()
    if text == "":
        raise RomanError("empty string is not a roman numeral")
    for ch in text:
        if ch not in _SINGLE:
            raise RomanError("invalid roman character: " + ch)
    total = 0
    i = 0
    length = len(text)
    while i < length:
        if i + 1 < length:
            pair = text[i:i + 2]
            if pair in _VALID_SUBTRACTIVE:
                total += _SINGLE[pair[1]] - _SINGLE[pair[0]]
                i += 2
                continue
        current = _SINGLE[text[i]]
        if i + 1 < length:
            nxt = _SINGLE[text[i + 1]]
            if current < nxt:
                raise RomanError("invalid subtractive pair: " + text[i:i + 2])
        total += current
        i += 1
    if total < _MIN_VALUE or total > _MAX_VALUE:
        raise RomanError("value out of range 1..3999")
    _check_canonical(text)
    return total


def _check_canonical(text):
    message = "not a canonical roman numeral: " + text

    # Rule 1: I, X, C and M appear at most three times in a row.
    for symbol in ("I", "X", "C", "M"):
        if symbol * 4 in text:
            raise RomanError(message)

    # Rule 2: V, L and D appear at most once in the whole string.
    for symbol in ("V", "L", "D"):
        if text.count(symbol) > 1:
            raise RomanError(message)

    # Rule 3: each of the six subtractive pairs at most once. The rest of the
    # rule, no smaller symbol before a larger one outside those six, is
    # already enforced while parsing.
    for pair in _VALID_SUBTRACTIVE:
        if text.count(pair) > 1:
            raise RomanError(message)

    # Read the string as a sequence of groups: a subtractive pair or a single
    # symbol. Each group carries its value and, for a pair, the value of the
    # subtracted symbol.
    groups = []
    i = 0
    while i < len(text):
        pair = text[i:i + 2]
        if pair in _VALID_SUBTRACTIVE:
            groups.append((_SINGLE[pair[1]] - _SINGLE[pair[0]], _SINGLE[pair[0]]))
            i += 2
        else:
            groups.append((_SINGLE[text[i]], None))
            i += 1

    # Rule 4: group values are non-increasing from left to right.
    for previous, current in zip(groups, groups[1:]):
        if current[0] > previous[0]:
            raise RomanError(message)

    # Rule 5: after a subtractive pair, every following group must be worth
    # less than the subtracted symbol.
    for index in range(len(groups)):
        subtracted = groups[index][1]
        if subtracted is None:
            continue
        for value, _ in groups[index + 1:]:
            if value >= subtracted:
                raise RomanError(message)


def _roundtrip_differs(value, text):
    return to_roman(value) != text


def _count_char(text, ch):
    total = 0
    for c in text:
        if c == ch:
            total += 1
    return total


def is_valid_roman(s):
    try:
        from_roman(s)
        return True
    except RomanError:
        return False


def add_roman(a, b):
    return to_roman(from_roman(a) + from_roman(b))


def subtract_roman(a, b):
    return to_roman(from_roman(a) - from_roman(b))
