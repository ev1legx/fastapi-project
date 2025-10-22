import pytest
from datetime import datetime
from app.models import Client, Parking, ClientParking


@pytest.fixture
def setup_test_data(db_session):
    client = Client(name="Test", surname="Tester", credit_card="1234-5678-9012-3456")
    parking = Parking(
        address="Main Street", opened=True, count_places=10, count_available_places=10
    )
    db_session.add_all([client, parking])
    db_session.commit()

    client_parking = ClientParking(
        client_id=client.id, parking_id=parking.id, time_in=datetime.utcnow()
    )
    db_session.add(client_parking)
    db_session.commit()

    return {"client": client, "parking": parking}


def test_get_clients_list(client):
    response = client.get("/clients")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_client_by_id(client, setup_test_data):
    client_id = setup_test_data["client"].id
    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id


def test_create_client(client):
    data = {
        "name": "Alice",
        "surname": "Smith",
        "credit_card": None,
        "car_number": "XYZ123",
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    json_resp = response.json()
    assert "id" in json_resp


def test_create_parking(client):
    data = {
        "address": "Park Lane 1",
        "opened": True,
        "count_places": 20,
        "count_available_places": 20,
    }
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    json_resp = response.json()
    assert "id" in json_resp


@pytest.mark.parking
def test_parking_entry(client, setup_test_data):
    client_id = setup_test_data["client"].id
    parking_id = setup_test_data["parking"].id
    response = client.post(
        "/client_parkings", params={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 400  # Клиент уже припаркован


@pytest.mark.parking
def test_parking_exit(client, setup_test_data):
    client_id = setup_test_data["client"].id
    parking_id = setup_test_data["parking"].id
    response = client.delete(
        "/client_parkings", params={"client_id": client_id, "parking_id": parking_id}
    )
    assert response.status_code == 200  # Успешный выход
