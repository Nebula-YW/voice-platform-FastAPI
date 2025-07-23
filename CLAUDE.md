# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management (UV)
- `uv sync` - Install dependencies from lock file
- `uv add package-name` - Add new dependency
- `uv add --dev package-name` - Add development dependency
- `uv run command` - Run command in project environment
- `uv pip compile pyproject.toml > requirements.txt` - Generate requirements.txt for production deployment (excludes dev dependencies)

### Running the Application
- `uv run uvicorn api.main:app --reload --port 3000` - Start development server
- Access API at http://localhost:3000
- Interactive docs at http://localhost:3000/api/v1/docs

### Testing
- `uv run pytest tests/` - Run all tests
- `uv run pytest tests/ --cov=api` - Run tests with coverage
- `uv run pytest tests/test_all.py -v` - Run specific test file with verbose output

### Code Quality
- `uv run ruff check .` - Run linter
- `uv run ruff format .` - Format code

## Architecture Overview

This is a FastAPI application optimized for Vercel deployment with serverless functions.

### Project Structure
- `api/main.py` - FastAPI app initialization, CORS middleware, and root endpoint
- `api/routers.py` - All API route handlers (health, echo, items CRUD, users)
- `api/schemas.py` - Pydantic models for request/response validation
- `tests/` - Test suite using pytest and TestClient
- `vercel.json` - Vercel serverless configuration
- `pyproject.toml` - Project dependencies managed by UV

### Key Components

**FastAPI App (`api/main.py`):**
- Configured with custom OpenAPI docs URLs (`/api/v1/docs`, `/api/v1/redoc`)
- CORS middleware configured for all origins (configure for production)
- All API routes prefixed with `/api/v1`

**Router System (`api/routers.py`):**
- Single router handling all endpoints
- In-memory storage for demo (items_db, users_db)
- Structured logging throughout
- Global ID counters for items and users

**Data Models (`api/schemas.py`):**
- Pydantic models with validation
- Separate Create/Response models for proper API design
- Timestamp fields auto-generated

### API Endpoints Structure
- Root: `/` - API information
- Health: `/api/v1/health`
- Echo: `/api/v1/echo`
- Items: `/api/v1/items` (full CRUD)
- Users: `/api/v1/users` (create, read, list)

### Deployment Configuration
- Vercel uses `requirements.txt` for deployment
- Development uses `uv.lock` for dependency management
- Function memory: 3009MB, max duration: 300s
- All routes handled by `/api/main` through rewrites

### Testing Strategy
- Uses FastAPI TestClient for API testing
- Comprehensive test coverage including validation, CRUD operations, and error cases
- Tests include pagination, duplicate handling, and complete workflows