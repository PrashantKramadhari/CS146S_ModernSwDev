# Test Runner Automation

Run the test suite with early exit on failure, and run coverage if all tests pass.

## Arguments
- `path`: (Optional) Path to a specific test file or directory. Defaults to `backend/tests`.

## Steps
1. Run pytest with early exit:
   ```bash
   pytest -q ${path:-backend/tests} --maxfail=1 -x
   ```
2. If the previous step succeeded, run coverage:
   ```bash
   pytest --cov=backend/app ${path:-backend/tests}
   ```
3. Summarize the results and suggest next steps if there were failures.
