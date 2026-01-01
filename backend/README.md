# Backend setup and migrations

The backend uses Alembic to manage the SQLAlchemy models for `User`, `Conversation`, and `Message`. The first revision lives at `backend/alembic/versions/0001_initial_models.py` and captures the current schema.

## Prepare a local environment
1. Create and activate a virtual environment inside `backend/`:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Point the database URL to your target database (defaults to `sqlite:///./chimera.db`). You can set `DATABASE_URL` in the environment or edit `alembic.ini`.

## Apply migrations
Use the repo-level helper to run Alembic with the bundled `alembic.ini`:
```bash
make db-upgrade
```
This target executes `alembic -c alembic.ini upgrade head` from the `backend/` directory so contributors can sync schema with a single command.

You can also run Alembic directly if you prefer manual control:
```bash
cd backend
source venv/bin/activate
alembic -c alembic.ini upgrade head
```

## Smoke-test connectivity
After applying migrations, verify that SQLAlchemy can create, read, update, and delete records by running the lightweight smoke test:
```bash
cd backend
source venv/bin/activate
python -m pytest tests/test_db_connectivity.py -q
```
This test spins up a temporary in-memory database with `SessionLocal` and performs a CRUD round trip against the `User` model.
