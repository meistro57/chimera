# Chimera Project Guide

## Commands
- **Full dev setup**: `make dev`
- **Backend dev server**: `make dev-backend` (runs uvicorn)
- **Frontend dev server**: `make dev-frontend` (runs vite)
- **Build all**: `make build`
- **Test backend**: `make backend-test` or `cd backend && python -m pytest [file::class::test_method]`
- **Test frontend**: `make frontend-test` (needs Jest setup)
- **Lint backend**: `make backend-lint` (Flake8)
- **Lint frontend**: `make frontend-lint`
- **Migrate DB**: `make migrate`
- **Clean up**: `make clean`

## Code Style
- **Python**: Snake_case for vars/functions, CamelCase for classes, Pydantic for types, try-except for errors, imports: stdlib > third-party > local.
- **JavaScript/JSX**: CamelCase for vars/functions, PascalCase for components, React hooks convention, async/await, Tailwind for CSS, ESLint rules.
- **General**: No comments unless complex logic, follow existing patterns in codebase.