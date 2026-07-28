import pytest
from sqlalchemy.orm import Session

from backend.database import engine
from backend.repository.legacy_systems import create_legacy_system

@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def legacy_system(db_session):
    return create_legacy_system(
        session=db_session,
        name="Test Legacy System",
        description="Used for webhook tests",
    )