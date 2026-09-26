from fastapi import FastAPI
from shifttestex.app.routers import router

app = FastAPI(title="BookingRooms")
    
app.include_router(router)