# Testing Life Cycle Workshop

**Jorge Bravo Vidal** — Software Engineering II

System under test: `src/roman/converter.py`, a roman numeral converter.
When the code and `SPECIFICATION.md` disagree, the specification is right.

---

## Summary

| | |
|---|---|
| Branch coverage | 64% → **100%** |
| Tests | 15 inherited → **77 total** |
| Final result | 77 passed, 0 failed |
| Defects found and fixed | **3** |
| Inherited tests modified | none |

---

## Part 1–2: Prepare and audit

The inherited suite passes with 15 tests and 64% branch coverage. It only checks
values the code already gets right, so it never touches the defects.

```
pytest --cov=roman.converter --cov-branch --cov-report=term-missing
# 68 stmts, 24 miss, 34 branch, 9 BrPart, 64%
```

---

## Part 3: Unit level (structural)

Tests derived from the source code of `to_roman`, lines 40 to 53.

### Control flow graph

The compound predicate of line 41 is split into two nodes, `41a` for
`not isinstance(n, int)` and `41b` for `isinstance(n, bool)`, so each condition
owns its own decision.

```
N = 17 nodes
E = 22 edges
V(G) = E - N + 2 = 22 - 17 + 2 = 7
```

### Basis set

| # | Path | Inverted decision | Input |
|---|---|---|---|
| P1 | src,40,41a,41b,43,45,47,48,49,53,snk | baseline | (infeasible) |
| P2 | src,40,41a,42,snk | 41a | `"X"` |
| P3 | src,40,41a,41b,42,snk | 41b | `True` |
| P4 | src,40,41a,41b,43,44,snk | 43 | `0` |
| P5 | src,40,41a,41b,43,45,46,snk | 45 | `4000` |
| P6 | src,...,49,50,49,53,snk | 49 | (infeasible) |
| P7 | src,...,49,50,51,52,50,49,53,snk | 50 | `1` |

P1 and P6 are infeasible: any `n` reaching node 49 is at least 1, and the entry
`(1, "I")` of `_PAIRS` guarantees the inner loop appends at least once.

### Definition-use pairs

| Pair (def, use) | Variable | Type |
|---|---|---|
| (40, 41a) (40, 41b) (40, 43) (40, 45) | `n` | p-use |
| (40, 48) | `n` | c-use |
| (47, 51) (47, 53) (51, 51) (51, 53) | `out` | c-use |
| (48, 50) | `remaining` | p-use |
| (48, 52) | `remaining` | c-use |
| **(52, 50)** | `remaining` | **p-use** |
| **(52, 52)** | `remaining` | **c-use** |
| (49, 50) | `value` | p-use |
| (49, 52) | `value` | c-use |
| (49, 51) | `symbol` | c-use |

The two pairs in bold are the ones created by the redefinition of `remaining`
inside the loop: the value produced at line 52 is re-tested by the predicate at
line 50 and consumed again at line 52 on the next iteration. `(47, 53)` is
infeasible, since `out` is always redefined by an append before line 53.

### Result

`tests/test_unit_structural.py` raises branch coverage from 64% to **100%**.
Four tests fail, all from the same defect in `_PAIRS`, fixed in Part 6.

---

## Part 4: Integration level

Section 7 defines `add_roman` and `subtract_roman` as compositions:

```
add_roman(a, b)  ->  from_roman(a) --+
                                     +-- sum --> to_roman(...) --> result
                     from_roman(b) --+                              |
                                                 is_valid_roman(result)
```

### Finding

`add_roman("II","II")` returns `IIII` where section 7 requires `IV`, because
`_PAIRS` holds `(5, "IV")` instead of `(4, "IV")` and, since `(5, "V")` precedes
it, that entry can never match.

The revealing contrast is in the execution log, on the same input:

| Test | Result |
|---|---|
| `test_add_roman_result_is_accepted_by_is_valid_roman[II-II]` | **PASSED** |
| `test_add_roman_result_is_canonical[II-II]` | **FAILED** |

The consistency requirement of section 7 holds only because `is_valid_roman`
never enforces the canonical form of section 4, so it accepts `IIII`. A second
defect masks the first, and `from_roman(to_roman(n)) == n` holds for all 3999
values while the system is wrong.

### Why the unit tests pass

- **`to_roman`**: the structural tests reach 100% branch coverage, but a control
  flow graph records which decisions exist, not which symbol a data table entry
  should carry. That lives only in the specification.
- **`from_roman`**: there is no canonicity check in the code, and coverage cannot
  report a branch that was never written.
- **`is_valid_roman`**: a faithful wrapper; it adds no defect of its own.
- **`add_roman` / `subtract_roman`**: one line each, correct arithmetic.

Each unit is consistent with itself. The defect surfaces only when the generator
and the validator are composed and judged against an external criterion.

`tests/spec_oracle.py` provides that criterion: it transcribes the five rules of
section 4 and imports nothing from `roman.converter`, because the specification
forbids using `to_roman(from_roman(s)) == s` as the oracle.

**Result:** 14 passed, 7 failed.

---

## Part 5: Acceptance level (functional)

Three criteria taken from the specification, in Given / When / Then form.

**AC1 (section 3).** *Given* that numerals arrive from a user-facing field where
stray blanks are common, *when* the user submits `"  IV  "`, *then* the system
reads it as 4, while `"X I"` is rejected.

**AC2 (sections 4 and 6).** *Given* that only the canonical form is accepted,
*when* a user enters `"IIII"` or `"XXXX"`, *then* `from_roman` raises `RomanError`
and `is_valid_roman` returns `False` without raising.

**AC3 (section 7).** *Given* a user who adds two roman numerals, *when* the user
adds `"II"` and `"II"`, *then* the system returns `"IV"`.

All three fail at 100% branch coverage.

### Why coverage cannot reveal these defects

Coverage measures which code was *executed*, not whether it is *correct*, and
each of these defects is code that does not exist. AC1 fails because `from_roman`
never calls `strip()`. AC2 fails because there is no canonicity check anywhere in
the module. AC3 fails because a constant is wrong while the entry holding it is
executed dutifully.

Adding the acceptance tests left coverage unchanged: they found three defects
while executing exactly the same lines as before.

---

## Part 6: Iteration

| Commit | Defect | Fix | Found by |
|---|---|---|---|
| `59ed588` | `_PAIRS` held `(5, "IV")`; unreachable, so `IV` was never emitted | `(4, "IV")` per section 2 | unit |
| `12f60d2` | `from_roman` accepted non-canonical strings, masking the defect above | new `_check_canonical`, applying the five rules of section 4 directly | integration |
| `aa01f1d` | `from_roman` did not tolerate leading or trailing whitespace | `s.strip().upper()` per section 3 | acceptance |

Suite green at **77 passed, 0 failed**. The 15 inherited tests in
`tests/test_converter.py` were neither modified nor deleted.

---

## Coverage

| Stage | Stmts | Miss | Branch | BrPart | Cover | Result |
|---|---|---|---|---|---|---|
| Part 2, inherited suite only | 68 | 24 | 34 | 9 | 64% | 15 passed |
| Part 3, structural unit tests | 68 | 0 | 34 | 0 | 100% | 41 passed, 4 failed |
| Parts 4–5, before the fixes | 68 | 0 | 34 | 0 | 100% | 57 passed, 20 failed |
| Part 6, after the fixes | 99 | 0 | 62 | 0 | 100% | 77 passed |

The middle rows are the point: the suite reached 100% branch coverage while 20
tests were still failing, and the integration and acceptance tests did not move
the number at all. Coverage bounds how much of the implementation the suite has
seen; only the specification can say whether what it saw was right.

The counts grow in the last row because the canonical-form fix added 31
statements and 28 branches to the module, not because the suite got stronger.

---

## Files

| Path | Contents |
|---|---|
| `tests/test_converter.py` | 15 inherited tests, unmodified |
| `tests/test_unit_structural.py` | Part 3, structural tests of `to_roman` |
| `tests/spec_oracle.py` | independent canonicity oracle, section 4 |
| `tests/test_integration.py` | Part 4, the `add_roman` collaboration |
| `tests/test_acceptance.py` | Part 5, the three acceptance criteria |

```bash
pytest --cov=roman.converter --cov-branch --cov-report=term-missing
```
