_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

_SUBTRACTIVE = {"IV": 4, "IX": 9, "XL": 40, "XC": 90, "CD": 400, "CM": 900}

_REPEATABLE = ("I", "X", "C", "M")
_NON_REPEATABLE = ("V", "L", "D")


def _groups(text):
    out = []
    i = 0
    while i < len(text):
        pair = text[i:i + 2]
        if pair in _SUBTRACTIVE:
            out.append((_SUBTRACTIVE[pair], _VALUES[pair[0]]))
            i += 2
        else:
            out.append((_VALUES[text[i]], None))
            i += 1
    return out


def is_canonical(s):
    if not isinstance(s, str):
        return False
    text = s.strip().upper()
    if text == "" or any(ch not in _VALUES for ch in text):
        return False

    # Rule 1: I, X, C and M appear at most three times in a row.
    for symbol in _REPEATABLE:
        if symbol * 4 in text:
            return False

    # Rule 2: V, L and D appear at most once in the whole string.
    for symbol in _NON_REPEATABLE:
        if text.count(symbol) > 1:
            return False

    # Rule 3: only the six subtractive pairs are allowed, each at most once,
    # and outside them no symbol may be followed by one of greater value.
    for pair in _SUBTRACTIVE:
        if text.count(pair) > 1:
            return False
    for i in range(len(text) - 1):
        left, right = text[i], text[i + 1]
        if _VALUES[left] < _VALUES[right] and left + right not in _SUBTRACTIVE:
            return False

    groups = _groups(text)

    # Rule 4: group values are non-increasing from left to right.
    for previous, current in zip(groups, groups[1:]):
        if current[0] > previous[0]:
            return False

    # Rule 5: after a subtractive pair, every following group must be worth
    # less than the subtracted symbol.
    for index, (_, subtracted) in enumerate(groups):
        if subtracted is None:
            continue
        for value, _ in groups[index + 1:]:
            if value >= subtracted:
                return False

    # Supported range of section 1.
    total = sum(value for value, _ in groups)
    return 1 <= total <= 3999
