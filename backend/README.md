# Backend setup and migrations

This backend uses Alembic to manage the SQLAlchemy models. To align a local database with the current `User`, `Conversation`, and `Message` schemas:

1. Create and activate a virtual environment inside `backend/`:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Point `DATABASE_URL` to your target database (defaults to `sqlite:///./chimera.db`).
3. Apply migrations with the repo-level helper:
   ```bash
   make db-upgrade
   ```
   The target runs `alembic -c alembic.ini upgrade head` against the configured database.

For manual runs, you can also execute Alembic directly:
```bash
cd backend
source venv/bin/activate
alembic -c alembic.ini upgrade head
```

After running migrations, the database will include the latest columns for authentication, conversation sharing, and message metadata alignment. A lightweight smoke test is available via `python -m pytest tests/test_db_connectivity.py` to verify connectivity.
