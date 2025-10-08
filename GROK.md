# GROK Project Notes

## Current Status (as of 10/8/2025)

- Adjusted SQLAlchemy models for SQLite: Used String(36) for UUIDs, JSON for JSON fields, removed ARRAY.

- Regenerated Alembic migration 'fd92c5af2c65_initial_migration_for_sqlite.py' and applied it successfully.

- Database schema now initialized in chimera.db with tables: ai_providers, users, conversations, messages.

## Pending TODOs from current_state_todo.md

- Backend: Implement DB writes in _save_and_broadcast_message, replace stubbed history.

- Data Layer: Create CRUD helpers, seed data.

- Providers: Harden config, fallbacks, streaming buffering.

- Frontend: Swap hardcoded IDs, persist messages, error states, styling.

- DevOps: Add lint/test to Makefile, .env.example.

- Testing: Add unit/integration tests.

## Next Immediate Action

Wire database persistence for messages and history retrieval in orchestrator.

