from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    name: str
    surname: str
    credit_card: Optional[str] = None
    car_number: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientOut(ClientBase):
    id: int
    class Config:
        orm_mode = True

class ParkingBase(BaseModel):
    address: str
    opened: Optional[bool] = True
    count_places: int
    count_available_places: int

class ParkingCreate(ParkingBase):
    pass

class ParkingOut(ParkingBase):
    id: int
    class Config:
        orm_mode = True
