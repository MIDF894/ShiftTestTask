from pydantic import BaseModel, ConfigDict, Field, field_validator, ConfigDict
from shifttestex.database.models import *
from enum import Enum
from datetime import time, date


class UserResponse(BaseModel):
	id: int
	username: str
	role: UserRole

	model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole

class RoomsEnum(int, Enum):
    room1 = 1
    room2 = 2
    room3 = 3
    room4 = 4
    room5 = 5

class TimeSlotsEnum(int, Enum):
    room1 = 1
    room2 = 2
    room3 = 3
    room4 = 4

class RoomResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

class TimeSlotResponse(BaseModel):
    id: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)

class RoomDetailResponse(RoomResponse):
    timeslots: list[TimeSlotResponse]

class BookingResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    timeslot_id: int
    booking_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingDateCreate(BaseModel):
    booking_date: date = Field(
        description="Дата бронирования (поддерживаются форматы: ДД.ММ.ГГГГ, ГГГГ-ММ-ДД)",
        examples=["25.09.2026"]
    )

    @field_validator("booking_date", mode="before")
    @classmethod
    def parse_custom_date_format(cls, value):
        if isinstance(value, str):
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    pass
            raise ValueError("Формат даты должен быть ДД.ММ.ГГГГ или ГГГГ-ММ-ДД")
        return value

    @field_validator("booking_date")
    @classmethod
    def validate_future_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Нельзя забронировать дату в прошлом")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "booking_date": "25.09.2026"
            }
        }
    )