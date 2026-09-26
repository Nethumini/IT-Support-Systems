# Backend Test-Suite Evidence - 26 September 2026

## Status

This is an interim clean run produced after implementing medium-risk approval authorization. It must be repeated after the final implementation commit is frozen.

## Command

```text
DEBUG=false ../venv/bin/python -m pytest -q --junitxml=evaluation/results/test-suite-20260926.xml
```

`DEBUG=false` was applied only to the test process because the surrounding development shell exposed an unrelated non-Boolean `DEBUG=release` value that the application settings correctly rejected.

## Result

- Tests collected and passed: **431**
- Failures: **0**
- Errors: **0**
- Skipped: **0**
- Runtime: **69.87 seconds**
- Machine timestamp: **2026-09-26T21:16:42+05:30**
- Detailed machine-readable record: `test-suite-20260926.xml`

The run emitted dependency and deprecation warnings, including timezone-naive `datetime.utcnow()` use and library migration notices. These warnings did not fail tests, but they should be tracked as maintenance work and must not be described as functional test failures.
