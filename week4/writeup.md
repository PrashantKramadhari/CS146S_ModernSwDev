# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
### Automation #1: Test Runner Slash Command
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the "Claude Code best practices" which recommends creating focused slash commands for repeated workflows. This automation streamlines the "test-then-coverage" loop.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Run tests efficiently and provide coverage data only if tests pass.
> **Inputs:** Optional `path` to a test file or directory.
> **Steps:**
> 1. Run `pytest` with `-x` (exit on first failure).
> 2. If successful, run `pytest-cov` to generate coverage reports.
> **Output:** Test results and coverage summary.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **Command:** `/test` or `/test path=backend/tests/test_main.py`
> **Expected Output:** Pytest output followed by a coverage table.
> **Safety:** This is a read-only automation that doesn't modify source code.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Manually typing long `pytest` commands and then manually running coverage if they pass.
> **After:** A single `/test` command handles the logic and reporting.

e. How you used the automation to enhance the starter application
> TODO: Describe how you used this to verify your changes.


### Automation #2: Lint & Format Slash Command
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the "Style and safety guardrails" example in `assignment.md`. It ensures that all code meets the project's formatting standards before submission.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Automatically fix formatting and linting issues.
> **Steps:**
> 1. Run `make format` (black).
> 2. Run `ruff check --fix`.
> 3. Run `make lint` to verify.
> **Output:** Summary of fixed issues and remaining lint errors.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **Command:** `/lint-fix`
> **Expected Output:** Output from black and ruff showing modified files.
> **Safety:** Modifies files in place. Recommended to run on a clean git state.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Running multiple `make` commands and manually fixing lint errors.
> **After:** A single command fixes most issues and reports the rest.

e. How you used the automation to enhance the starter application
> TODO: Describe how you used this to clean up your code.


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> TODO

b. Design of each automation, including goals, inputs/outputs, steps
> TODO

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> TODO

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

e. How you used the automation to enhance the starter application
> TODO
