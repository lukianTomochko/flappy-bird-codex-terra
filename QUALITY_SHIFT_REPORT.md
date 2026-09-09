# Code quality shift report

## Verification and metrics

Baseline and final measurements were collected with Python 3.11, `pytest`,
Ruff 0.16.6, and Black 26.5. The Ruff quality gate is intentionally scoped to
PEP 8/Pyflakes/Bugbear/McCabe (`E,F,B,C90`), as requested. Ruff's language
server is an editor service rather than a metrics command, so `ruff check`
was used as its CLI equivalent.

| Metric | Before | After | Change |
| --- | ---: | ---: | --- |
| Pytest cases | 9 passed | 9 passed | Green throughout |
| `src` coverage | 45% | 46% | +1 percentage point |
| Ruff `E,F,B,C90` violations | 12 | 0 | -12 |
| McCabe `C90` violations | 0 | 0 | No functions exceed configured complexity limits |
| Full Ruff findings | 49 | 26 | -23 |
| Black files requiring formatting | 6 | 0 | Fully compliant |

The remaining 26 full-Ruff findings are optional modernization suggestions:
PEP 585 built-in collection annotations and explicit optional typing. They do
not belong to the requested quality gate and were left untouched to avoid a
wide, low-value type-annotation churn.

## Refactoring log

- Declared the public exports of `src.entities` and `src.utils` with
  `__all__`. This preserves the package API while removing all 12 Pyflakes
  false-positive unused-import findings.
- Cached the game-over leaderboard font in `Score.__init__` instead of
  recreating a system font on every rendered game-over frame. This reduces
  repeated allocation in the heaviest measured UI frame.
- Replaced `list(generator)` constructions with direct list comprehensions.
  The result is equivalent and removes generator-wrapper allocation in
  image-loading and collision setup.
- Parsed `DEBUG` as an explicit boolean value (`1`, `true`, or `yes`) rather
  than treating any non-empty string, including `DEBUG=False`, as enabled.
- Flattened the nested restart condition in the game-over loop without
  changing its input or floor-contact requirements.
- Ran Black with `--target-version py39`, matching the project's supported
  Python range, then applied Ruff's safe fixes. Pytest plus coverage ran after
  each change set; no rollback was required.

## Final commands

```cmd
python -m pytest -q --cov=src --cov-report=term
python -m ruff check . --select E,F,B,C90
python -m black --target-version py39 --check .
```
