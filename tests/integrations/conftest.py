from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal, engine


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
