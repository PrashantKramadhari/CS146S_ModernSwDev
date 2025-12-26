# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Full-stack "developer's command center" application using FastAPI backend with SQLite/SQLAlchemy and vanilla JavaScript frontend. Built as a learning environment for Claude Code automation features (SubAgents, slash commands, MCP servers).

## Essential Commands

### Running the Application
- Start server: `make run` (defaults to http://127.0.0.1:8000)
- Override host/port: `HOST=0.0.0.0 PORT=3000 make run`
- Frontend: http://localhost:8000
- API Documentation: http://localhost:8000/docs (interactive Swagger UI)
- OpenAPI schema: http://localhost:8000/openapi.json

### Testing
- Run all tests: `make test` or `PYTHONPATH=. pytest -q backend/tests`
- Run specific test file: `PYTHONPATH=. pytest backend/tests/test_notes.py`
- Run with early exit on failure: `pytest -q backend/tests --maxfail=1 -x`
- Run with coverage: `pytest --cov=backend/app backend/tests`
- Verbose output: Add `-v` flag to any pytest command

### Code Quality
- Format code: `make format` (runs black + ruff --fix)
- Lint without fixing: `make lint` (ruff check only)
- Pre-commit hooks: `pre-commit install` then `pre-commit run --all-files`

### Database
- Reseed database: `make seed` (applies data/seed.sql)
- Database location: `./data/app.db` (SQLite)
- Database auto-seeds on first run via startup event in main.py

## Architecture

### Backend Structure (`backend/app/`)
- **`main.py`**: FastAPI application entry point
  - Registers routers for notes and action items
  - Mounts static frontend at `/static`
  - Serves `frontend/index.html` at root `/`
  - Startup event creates tables and applies seed data

- **`db.py`**: Database session management
  - SQLAlchemy engine and sessionmaker
  - `get_db()`: Dependency injection for routes (yields session, commits on success, rolls back on error)
  - `get_session()`: Context manager for direct database access
  - `apply_seed_if_needed()`: Automatically seeds database on first run

- **`models.py`**: SQLAlchemy ORM models
  - `Note`: id, title, content
  - `ActionItem`: id, description, completed (boolean)

- **`schemas.py`**: Pydantic models for request/response validation
  - Define request payloads and response shapes
  - Used by FastAPI for automatic validation and OpenAPI docs

- **`routers/`**: API route handlers
  - `notes.py`: CRUD endpoints for notes (`/notes`)
  - `action_items.py`: CRUD endpoints for action items (`/action-items`)
  - Each router uses `Depends(get_db)` for database sessions

- **`services/`**: Business logic and utilities
  - `extract.py`: Text parsing utilities (e.g., extracting action items from notes)

### Frontend Structure (`frontend/`)
- Vanilla JavaScript (no build toolchain)
- `index.html`: Single-page UI
- `app.js`: Fetch-based API client
- `styles.css`: Basic styling
- Served as static files by FastAPI

### Testing Structure (`backend/tests/`)
- `conftest.py`: Pytest fixtures (test database session, test client)
- `test_*.py`: Test files corresponding to routers/services
- Uses in-memory SQLite for test isolation

### Data (`data/`)
- `app.db`: SQLite database (auto-created)
- `seed.sql`: Initial data loaded on first run

## Development Workflows

### Adding a New Endpoint
1. Write a failing test in `backend/tests/test_*.py`
2. Add Pydantic schemas to `schemas.py` (request/response models)
3. Implement the route handler in the appropriate router (`routers/*.py`)
4. Run tests: `make test`
5. Verify linting: `make lint` and format: `make format`
6. Test manually via `/docs` or the frontend

### SubAgent Workflow
This repo includes two specialized SubAgents in `.claude/agents/`:

- **TestAgent**: Quality assurance specialist
  - Writes comprehensive test cases for new features
  - Identifies edge cases and potential bugs
  - Reports test results with detailed logs
  - Use when you need test coverage for a feature

- **CodeAgent**: Implementation specialist
  - Implements features based on requirements and failing tests
  - Refactors code for maintainability and performance
  - Ensures code follows style guidelines (black/ruff)
  - Use when you need to implement a feature with passing tests

**Typical SubAgent Flow**:
1. TestAgent writes failing tests for a new feature
2. CodeAgent implements code to make tests pass
3. TestAgent verifies all tests pass
4. CodeAgent runs `make lint` and `make format` to finalize

### Custom Slash Commands
Available in `.claude/commands/`:

- **`/tests`**: Test runner with coverage
  - Runs pytest with early exit on failure
  - If tests pass, runs coverage report
  - Accepts optional path argument: `/tests backend/tests/test_notes.py`

- **`/lint-fix`**: Automated formatting and linting
  - Runs `make format` to fix style issues
  - Runs ruff with auto-fix
  - Verifies everything is clean with `make lint`
  - Reports any remaining issues

## Key Patterns and Conventions

### Database Sessions
- Routes use `db: Session = Depends(get_db)` for automatic session management
- Direct access (e.g., seed scripts) uses `with get_session() as db:`
- Always commit on success, rollback on exception (handled automatically)

### Error Handling
- Use FastAPI's `HTTPException` for API errors
- Common patterns: 404 for not found, 400 for validation errors, 500 for server errors

### Code Style
- Black for formatting (line length 88)
- Ruff for linting (configured in pyproject.toml or ruff.toml if present)
- Pre-commit hooks enforce style on commit
- Always run `make format` before `make lint`

### Testing
- Use pytest fixtures from `conftest.py` for test database and client
- Tests should be isolated (each test gets fresh database state)
- Use descriptive test names: `test_create_note_success`, `test_get_note_not_found`
- Test both success and error cases

## Environment Setup
- Python environment: `conda activate cs146s` (conda environment name from assignment)
- PYTHONPATH must include project root for imports to work correctly
- Environment variables: Set `DATABASE_PATH` to override default database location

## Important Files
- `assignment.md`: Original assignment requirements and context
- `writeup.md`: Documentation of automations built for this project
- `docs/TASKS.md`: Sample tasks for practicing agent-driven workflows
- `pre-commit-config.yaml`: Pre-commit hook configuration (black, ruff, basic file checks)
