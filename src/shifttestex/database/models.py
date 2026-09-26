import enum
from datetime import datetime

from sqlalchemy import Date, String, Enum, ForeignKey, Time, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
	pass

class UserRole(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    ADMIN = "ADMIN"

class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
	hashed_password: Mapped[str] = mapped_column(String(255))
	role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum = False), default=UserRole.EMPLOYEE)

# Создаются в бд зараннее
class Room(Base):
	__tablename__ = "rooms"
	
	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(100))
	description: Mapped[str | None]

	timeslots: Mapped[list["TimeSlot"]] = relationship("TimeSlot", back_populates="room", cascade="all, delete-orphan")

# Создаются в бд зараннее
class TimeSlot(Base):
	__tablename__ = "timeslots"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

	start_time: Mapped[datetime.time] = mapped_column(Time)
	end_time: Mapped[datetime.time] = mapped_column(Time)
	room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

	room: Mapped["Room"] = relationship("Room", back_populates="timeslots")

class Booking(Base):
	__tablename__ = "bookings"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
	timeslot_id: Mapped[int] = mapped_column(ForeignKey("timeslots.id"))
	booking_date: Mapped[datetime.date] = mapped_column(Date)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)