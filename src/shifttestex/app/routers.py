from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete
from shifttestex.database.db import session
from shifttestex.database.models import *
from shifttestex.app.schemas import *
from shifttestex.app.security import *

router = APIRouter(tags = ["Routers"])

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await get_authenticate_user_from_db(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(user)
    return Token(access_token=access_token, token_type="bearer", role=user.role)


@router.get("/users/me/", response_model=UserResponse)
async def get_myself(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return current_user


@router.get("/users/me/bookings/", response_model = list[BookingResponse])
async def read_my_rooms(current_user: Annotated[User, Depends(get_current_user)]):
    async with session() as db:
        if current_user.role == "ADMIN":
            query = await db.execute(select(Booking))
        else:
            query = await db.execute(select(Booking).where(Booking.user_id == current_user.id).order_by(Booking.booking_date.desc())) 
        return query.scalars().all()

@router.get("/rooms/", response_model = list[RoomResponse])
async def read_rooms(current_user: Annotated[User, Depends(get_current_user)]):
    async with session() as db:
        rooms = await db.execute(select(Room))
        return rooms.scalars().all()

@router.get("/rooms/{room_id}/", response_model=RoomDetailResponse)
async def get_room(room_id: RoomsEnum, current_user: Annotated[User, Depends(get_current_user)]):
    async with session() as db:
        query = (select(Room).where(Room.id == room_id).options(selectinload(Room.timeslots)))
        result = await db.execute(query)
        room = result.scalar_one_or_none()

        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Комната не найдена")

        return room

@router.get("/rooms/{room_id}/{timeslot_id}/", response_model=TimeSlotResponse)
async def get_timeslot(room_id: RoomsEnum, timeslot_id: TimeSlotsEnum, current_user: Annotated[User, Depends(get_current_user)]):
    async with session() as db:
        query = (select(Room).where(Room.id == room_id).options(selectinload(Room.timeslots)))
        result = await db.execute(query)
        room = result.scalar_one_or_none()

        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Комната не найдена")

        return room.timeslots[timeslot_id - 1]

@router.post("/rooms/{room_id}/{timeslot_id}/booking/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking_path(room_id: RoomsEnum, timeslot_id: TimeSlotsEnum, booking_data: BookingDateCreate, current_user: Annotated[User, Depends(get_current_user)]):
    async with session() as db:

        query = (select(Room).where(Room.id == room_id).options(selectinload(Room.timeslots)))
        result = await db.execute(query)
        select_timeslot = result.scalar_one_or_none().timeslots[timeslot_id - 1].id

        existing_booking = await db.scalar(select(Booking).where(Booking.room_id == room_id, Booking.timeslot_id == select_timeslot, Booking.booking_date == booking_data.booking_date))
        if existing_booking:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Слот этой комнаты уже забронирован на выбранную дату")

        new_booking = Booking(user_id = current_user.id, room_id = room_id, timeslot_id = select_timeslot, booking_date = booking_data.booking_date)
        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)

        return new_booking

@router.delete("/rooms/booking/{booking_id}/", status_code = status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    async with session() as db:
        
        if current_user.role != "ADMIN":
            stmt = await db.execute(delete(Booking).where(Booking.id == booking_id, Booking.user_id == current_user.id))
        else:
            stmt = await db.execute(delete(Booking).where(Booking.id == booking_id))           

        await db.commit()

        if stmt.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено, или возможно у вас недостаточно прав")