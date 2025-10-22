import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.models import Client, ClientParking, Parking


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.create_all(bind=connection)  # можно опустить для in-memory!
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client(db_session):
    db_session.query(ClientParking).delete()
    db_session.query(Client).delete()
    db_session.query(Parking).delete()
    db_session.commit()
    with TestClient(app) as test_client:
        yield test_client
