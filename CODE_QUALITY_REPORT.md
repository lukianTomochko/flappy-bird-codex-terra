# Code quality and optimization report

## Scope

This review covers the high-score persistence and dynamic-difficulty work,
plus a small safety refactor in pipe lifecycle management. The game rules,
score ordering, difficulty thresholds, and UI behaviour are unchanged.

## Metrics

| Metric | Before refactor | After refactor | Notes |
| --- | ---: | ---: | --- |
| Python files | 23 | 23 | Source, tests, and `main.py` |
| Production LOC | 834 | 847 | The increase is documentation and one shared validation helper. |
| Total Python LOC | 920 | 933 | Includes the existing 9-test feature suite. |
| Feature test cases | 9 | 9 | No tests were added or removed. |
| Prior recorded coverage | 58% | Not remeasured | The existing project result exceeds the 20% requirement. |
| Flake8 configured complexity cap | 10 | 10 | Set in `.flake8`; lint could not be executed locally. |

LOC was measured with PowerShell's `Get-ChildItem` and `Measure-Object`.
The coverage figure is the previously recorded run for the unchanged suite;
it is not presented as a fresh measurement.

## Improvements made

1. **Single leaderboard validation policy**
   - Added `normalize_high_scores()` in `src/utils/high_scores.py`.
   - Loading, saving, and in-memory score recording now use the same sorting,
     top-five, and non-negative-integer policy.
   - Boolean values are explicitly rejected even though Python treats `bool` as
     a subclass of `int`.

2. **Safe pipe cleanup**
   - `Pipes.remove_old_pipes()` now filters upper/lower pipes as pairs instead
     of removing elements while iterating over each list.
   - This prevents consecutive off-screen pipes from being skipped and keeps
     upper/lower pipe collections aligned.
   - `can_spawn_pipes()` now handles an empty pipe list before reading its last
     element, making the spawn path resilient to cleanup edge cases.

3. **Maintainability annotations**
   - Added return types to pipe creation and lifecycle methods, and concise
     docstrings where behaviour is non-obvious.

## Validation

`git diff --check` completed successfully after the refactor, so the patch has
no whitespace errors.

The requested Python commands could not run in this environment:

```text
py -3.11 --version
# No installed Python found!
```

The Windows launcher is present, but it has no installed Python runtime.
Consequently, `flake8`, `unittest`, and a fresh `coverage` report are pending a
local Python installation. Run the following from the repository root once
Python 3.11 and development dependencies are available:

```cmd
py -3.11 -m flake8 src tests main.py
py -3.11 -m coverage run -m unittest discover -s tests -v
py -3.11 -m coverage report
```
