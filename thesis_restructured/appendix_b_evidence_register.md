# Appendix B - Final Evaluation Evidence Register

## B.1 Purpose

This appendix identifies the evidence used for the quantitative and operational claims in Chapters 4-6. It provides a reproducibility index without reproducing raw logs, secrets, private paths, or endpoint command values in the thesis. The evaluated source baseline was commit `cc655c3411ea96e67740e04b9c36df47cdfba064` (`cc655c3`), with tree `612f122e2f6514fc5d2716353a1c1fffd5c42751`.

## B.2 Evidence Packages

| Evidence package | Scope | Principal retained evidence |
| --- | --- | --- |
| `autoops-final-evidence-cc655c3-20260927` | Offline automated and comparative evaluation | Complete Pytest output and JUnit XML; 518-test result; 20 focused safety tests; 288 comparative records; summaries, metadata, recalculation output, and SHA-256 manifest |
| `autoops-final-retrieval-cc655c3-20260927` | Single authorised live retrieval run | Thirty per-query records; Hit@1, Hit@3, MRR, scores, timings, run metadata, integrity check, and SHA-256 manifest |
| `autoops-final-windows-cc655c3-20260927` | Controlled real-endpoint evaluation | Windows and PowerShell metadata; names-only diagnostic; approval and execution trace; observed postcondition failure; fingerprint-verified rollback; cleanup evidence; audit events; integrity metadata and SHA-256 manifest |

Each package was created without overwriting the earlier evidence. Its manifest was checked after collection. The repository remained at `cc655c3` with a clean working tree during the final retrieval and Windows evidence runs.

## B.3 Versioned Evaluation Inputs

| Input | SHA-256 |
| --- | --- |
| Retrieval query set | `e373d94761351ca14db77e0ed44c1b8f78c46063bedf196a4305e1a1302d7389` |
| Thirty-article knowledge dataset | `d9002cf4c60fe3c37bbd39aa3ab47f6bfb96e5a10344fd3f4b5dbaacf2c0d4ec` |
| Frozen Python requirements | `6fec67ebe1c99b74f32dd72cb5c6b67ccb59e513f688f26d8cce532501d36596` |

The comparative input consisted of the 32 labelled scenarios listed in Appendix A. Each was evaluated under three conditions and repeated three times. The author-labelled nature of both the scenarios and retrieval queries is a stated validity limitation rather than independent ground truth.

## B.4 Privacy and Integrity Boundaries

Credentials, environment files, databases, approval tokens, device-secret hashes, and raw startup commands were excluded from the retained thesis evidence. The live embedding run transmitted only the 30 query strings and each article's title plus issue pattern. The Windows diagnostic returned startup-item names only. Startup recovery verification compared locally generated SHA-256 fingerprints; the associated command values did not leave the endpoint.

The manifests establish whether the retained files changed after collection. They do not make the application audit log cryptographically tamper-evident, and the endpoint agent does not provide hardware-backed attestation. These boundaries are reflected in the limitations reported in Chapter 6.
