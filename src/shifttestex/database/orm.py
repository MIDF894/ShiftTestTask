from shifttestex.database.models import *
from shifttestex.database.db import engine, session
from datetime import time
from pwdlib import PasswordHash



# Gemini i love you
async def StartDb():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Все таблицы успешно созданы в БД!")

    async with session() as s:
        s.add_all([
            User(username = "RedBill", hashed_password = PasswordHash.recommended().hash("admin"), role = UserRole.ADMIN),
            User(username = "Dildojohn", hashed_password = PasswordHash.recommended().hash("1234")),
            User(username = "MalenKihren", hashed_password = PasswordHash.recommended().hash("4321")),
            
            Room(name = "Комната 1", description = "Вводная комната", timeslots = [
                TimeSlot(start_time = time(9), end_time = time(11)),
                TimeSlot(start_time = time(12), end_time = time(14)),
                TimeSlot(start_time = time(15), end_time = time(17)),
                TimeSlot(start_time = time(18), end_time = time(20))
            ]), 
            Room(name = "Комната 2(мини)", description = "Маленькая комната", timeslots = [
                TimeSlot(start_time = time(9), end_time = time(11)),
                TimeSlot(start_time = time(12), end_time = time(14)),
                TimeSlot(start_time = time(15), end_time = time(17)),
                TimeSlot(start_time = time(18), end_time = time(20))
            ]),
            Room(name = "Комната 3(стандарт)", description = "Стандартная комната", timeslots = [
                TimeSlot(start_time = time(9), end_time = time(11)),
                TimeSlot(start_time = time(12), end_time = time(14)),
                TimeSlot(start_time = time(15), end_time = time(17)),
                TimeSlot(start_time = time(18), end_time = time(20))
            ]),
            Room(name = "Комната 4(студия)", description = "Просторная комната студия", timeslots = [
                TimeSlot(start_time = time(9), end_time = time(11)),
                TimeSlot(start_time = time(12), end_time = time(14)),
                TimeSlot(start_time = time(15), end_time = time(17)),
                TimeSlot(start_time = time(18), end_time = time(20))
            ]),
            Room(name = "Комната 5", timeslots = [
                TimeSlot(start_time = time(9), end_time = time(11)),
                TimeSlot(start_time = time(12), end_time = time(14)),
                TimeSlot(start_time = time(15), end_time = time(17)),
                TimeSlot(start_time = time(18), end_time = time(20))
                ]),
            ])
        print("Чето insertнулось")
        await s.commit()