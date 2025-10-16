import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import Client, Parking, ClientParking
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределение зависимости get_db для тестов
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db):
    # Очистка БД перед тестами
    db.query(ClientParking).delete()
    db.query(Client).delete()
    db.query(Parking).delete()
    db.commit()

    yield TestClient(app)

@pytest.fixture(scope="module")
def setup_test_data(db):
    client = Client(name="Test", surname="Tester", credit_card="1111-2222-3333-4444", car_number="XYZ123")
    parking = Parking(address="Test Address", opened=True, count_places=10, count_available_places=10)
    db.add_all([client, parking])
    db.commit()
    cp = ClientParking(client_id=client.id, parking_id=parking.id, time_in=datetime.utcnow(), time_out=None)
    db.add(cp)
    db.commit()

    return {"client": client, "parking": parking, "client_parking": cp}
