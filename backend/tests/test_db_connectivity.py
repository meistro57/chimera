# backend/tests/test_db_connectivity.py
"""Lightweight database connectivity smoke test."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.user import User


def test_sessionlocal_crud_roundtrip() -> None:
    """Verify CRUD operations against a temporary in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Prepare schema for the isolated database.
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        # Create
        user = User(
            username="smoke-user",
            email="smoke@example.com",
            hashed_password="secret",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.id

        # Read
        fetched_user = session.query(User).filter_by(id=user.id).one()
        assert fetched_user.username == "smoke-user"

        # Update
        fetched_user.username = "updated-user"
        session.commit()
        session.refresh(fetched_user)
        assert (
            session.query(User.username).filter_by(id=user.id).scalar() == "updated-user"
        )

        # Delete
        session.delete(fetched_user)
        session.commit()
        assert session.query(User).count() == 0
    finally:
        # Clean up resources to avoid cross-test contamination.
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
