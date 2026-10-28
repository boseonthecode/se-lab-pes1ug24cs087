# Lab 5 - Known Issues

The following issues were identified in `digital_wallet.py` using Bandit, Pylint, and Flake8 before the fixes were applied. High and medium severity findings are listed first.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|-------------|
| Weak password hashing | Bandit B324 (High) | 14 | The PIN was hashed with SHA-1, which is not suitable for security-sensitive hashing. | Replaced SHA-1 with SHA-256 in `hash_pin`. |
| Insecure temporary file creation | Bandit B306 (Medium) | 60 | `tempfile.mktemp` creates a predictable filename and is vulnerable to race conditions. | Replaced `mktemp` with `tempfile.mkstemp` and closed the returned descriptor immediately. |
| Hardcoded gateway secret | Bandit B105 (Low) | 6 | The gateway secret was embedded directly in the source code. | Read the secret from the `GATEWAY_SECRET` environment variable instead. |
| Insecure OTP generation | Bandit B311 (Low) | 64 | The OTP used `random`, which is not cryptographically secure. | Replaced `random.randint` with `secrets.randbelow`. |
| Mutable default argument | Pylint W0102 (Bug) | 17 | The default `log=[]` list was shared across calls, so data could leak between invocations. | Changed the default to `None` and initialized a new list inside the function. |
| Global statement | Pylint W0603 | 28 | `set_daily_limit` modified `daily_limit` using a `global` statement. | Stored the daily limit in the `wallet` dictionary and removed the global variable. |
| Non-standard naming | Pylint C0103 | 9, 13, 17, 27, 32, 45, 50, 54, 58, 78 | Function, argument, and variable names used camelCase or lowercase constant naming. | Renamed identifiers to snake_case and used `UPPER_CASE` where appropriate. |
| Missing documentation | Pylint C0114/C0116 | 1, 13-63 | The module and its functions lacked docstrings. | Added a module docstring and concise docstrings for each function. |
| Unused argument | Pylint W0613 | 50 | The `merchantType` argument in `cashbackFor` was never used. | Renamed it to `_merchant_type` to mark it intentionally unused. |
| PEP 8 formatting violations | Flake8 E261/E225/E231/E305 | 76, 78, 79, 80 | Inline comments and operators were spaced incorrectly, a comma lacked a following space, and two blank lines were missing before the top-level call. | Corrected spacing, added the missing blank lines, and wrapped an overlong line. |

## Verification After Fixes

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.69/10 | 10.00/10 |
| Bandit | 4 issues (1 high, 1 medium, 2 low) | 0 issues |
| Flake8 | 4 violations | 0 violations |
