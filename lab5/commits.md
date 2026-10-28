# Lab 5 - Commit History

The fixes were committed incrementally in the nested assignment repository (`lab5/L5_29_digital_wallet`) so that each static analysis tool has its own commit.

Base commit: `0d188e2` - `Initial commit`

| Commit | Date | Message | Description |
|--------|------|---------|-------------|
| `1e48589` | 2026-10-28 21:29:12 +0530 | Fix security issues identified by Bandit | Replaced SHA-1 with SHA-256 for PIN hashing, replaced `random.randint` with `secrets.randbelow` for OTP generation, replaced `tempfile.mktemp` with `tempfile.mkstemp` and closed the descriptor, and removed the hardcoded gateway secret in favor of an environment variable. Bandit result: 4 issues reduced to 0. |
| `9421f71` | 2026-10-28 21:29:34 +0530 | Fix code quality issues identified by Pylint to achieve score > 9.5 | Added module and function docstrings, renamed functions and variables to snake_case, replaced the mutable default argument with `None`, moved the daily limit into the `wallet` dictionary to remove the `global` statement, marked the unused cashback argument intentionally unused, and cleaned up the final output formatting. Pylint score: 5.69/10 increased to 10.00/10. |
| `da4b494` | 2026-10-28 21:29:56 +0530 | Fix formatting and PEP 8 style issues identified by Flake8 | Fixed inline-comment spacing, operator and comma spacing, added the required blank lines before the top-level call, and wrapped an overlong list comprehension. Flake8 result: 4 violations reduced to 0. |

## Notes

- Commit `1e48589` changed only `digital_wallet.py` with 8 insertions and 5 deletions.
- Commit `9421f71` changed only `digital_wallet.py` with 38 insertions and 27 deletions.
- Commit `da4b494` changed only `digital_wallet.py` with 7 insertions and 3 deletions.
- The nested repository remains local and is excluded from the outer submission repository by `.gitignore`.
