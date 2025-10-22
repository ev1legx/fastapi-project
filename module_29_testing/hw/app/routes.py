
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, ClientParking, Parking
from app.schemas import ClientCreate, ClientOut, ParkingCreate, ParkingOut

router = APIRouter()


@router.get("/clients", response_model=List[ClientOut])
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()


@router.get("/clients/{client_id}", response_model=ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).get(client_id)
    if not client:
        raise HTTPException(status_code=404,
                            detail="Client not found")
    return client


@router.post("/clients", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.post(
    "/parkings", response_model=ParkingOut, status_code=status.HTTP_201_CREATED
)
def create_parking(parking: ParkingCreate, db: Session = Depends(get_db)):
    db_parking = Parking(**parking.dict())
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking


@router.post("/client_parkings", status_code=status.HTTP_201_CREATED)
def parking_entry(client_id: int, parking_id: int, db: Session = Depends(get_db)):
    parking = db.query(Parking).get(parking_id)
    if not parking or not parking.opened or parking.count_available_places <= 0:
        raise HTTPException(
            status_code=400,
            detail="Parking closed or no available places"
        )

    client = db.query(Client).get(client_id)
    if not client:
        raise HTTPException(status_code=404,
                            detail="Client not found")

    cp = (
        db.query(ClientParking)
        .filter_by(client_id=client_id, parking_id=parking_id, time_out=None)
        .first()
    )
    if cp:
        raise HTTPException(status_code=400,
                            detail="Client already parked here")

    parking.count_available_places -= 1
    cp = ClientParking(
        client_id=client_id, parking_id=parking_id, time_in=datetime.utcnow()
    )
    db.add(cp)
    db.commit()

    return {"message": "Entry logged"}


@router.delete("/client_parkings", status_code=200)
def parking_exit(client_id: int, parking_id: int, db: Session = Depends(get_db)):
    cp = (
        db.query(ClientParking)
        .filter_by(client_id=client_id, parking_id=parking_id, time_out=None)
        .first()
    )
    if not cp:
        raise HTTPException(status_code=404,
                            detail="No active parking found")

    client = db.query(Client).get(client_id)
    if not client or not client.credit_card:
        raise HTTPException(status_code=400,
                            detail="No credit card linked")

    cp.time_out = datetime.utcnow()
    if cp.time_in is not None and cp.time_out < cp.time_in:
        raise HTTPException(
            status_code=400,
            detail="Time out cannot be earlier than time in"
        )

    parking = db.query(Parking).get(parking_id)
    parking.count_available_places += 1

    db.commit()
    return {"message": "Exit logged and payment processed"}
