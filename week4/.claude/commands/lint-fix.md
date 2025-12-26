# Lint and Format Automation

Automatically format the code and fix linting issues.

## Steps
1. Run formatting:
   ```bash
   make format
   ```
2. Run linting with auto-fix:
   ```bash
   ruff check --fix backend/app
   ```
3. Verify that everything is clean:
   ```bash
   make lint
   ```
4. Report any remaining issues that couldn't be auto-fixed.
