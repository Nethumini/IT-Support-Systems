# Backend Test-Suite Evidence - 26 September 2026 (Interim Update)

## Status

This is the latest interim full-suite run after adding the end-to-end and prompt/tool-safety cases, inspectable scenario-label metadata, fingerprint-based startup rollback verification, and names-only startup diagnostics. It must be repeated after the final implementation commit is frozen.

## Command

```text
DEBUG=false ../venv/bin/python -m pytest -q --junitxml=evaluation/results/test-suite-interim-20260926.xml
```

## Result

- Tests passed: **501/501**
- Failures: **0**
- Errors: **0**
- Skipped: **0**
- Runtime: **74.547 seconds**
- Timestamp: **2026-09-26T23:03:25.806196+05:30**
- Machine-readable evidence: `test-suite-interim-20260926.xml`

The run emitted 1,304 dependency and deprecation warnings. These warnings did not fail tests and must not be represented as functional failures. The working tree was not yet the frozen final research version, so this result supports implementation progress but is not the final thesis run.
