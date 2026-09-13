from collections.abc import Generator

import pytest
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal


@pytest.fixture
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    session = SessionLocal(bind=db_connection)
    try:
        yield session
    finally:
        session.close()
