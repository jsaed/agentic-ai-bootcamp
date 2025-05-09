from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import random
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

# Initialize FastAPI app
app = FastAPI(
    title="Taxi Booking API",
    description="API for Cab booking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCESS_TOKEN = "R4Nd0mT0k3n"
latest_rides = []
confirmed_ride = None

class BookingRequest(BaseModel):
    current_location: str
    destination: str

class RideOption(BaseModel):
    name: str
    price: int
    arrival_time: int

class RideResponse(BaseModel):
    current_location: str
    destination: str
    ride_options: List[RideOption]

class ConfirmRequest(BaseModel):
    option_index: int

class ConfirmResponse(BaseModel):
    message: str
    chosen_ride: RideOption

class CancelResponse(BaseModel):
    message: str

@app.post("/rides", response_model=RideResponse)
def get_ride_options(request: BookingRequest, token: str = Header(...)):
    if token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token provided.")

    cheaper_price = random.randint(20, 40)
    medium_price = random.randint(cheaper_price + 1, 65)
    expensive_price = random.randint(medium_price + 1, 87)

    ride_options = [
        RideOption(name="Uber X", price=cheaper_price, arrival_time=random.randint(1, 15)),
        RideOption(name="Uber Comfort", price=medium_price, arrival_time=random.randint(1, 15)),
        RideOption(name="Uber Black", price=expensive_price, arrival_time=random.randint(1, 15))
    ]

    global latest_rides, confirmed_ride
    latest_rides = ride_options
    confirmed_ride = None

    return RideResponse(
        current_location=request.current_location,
        destination=request.destination,
        ride_options=ride_options
    )

@app.post("/confirm", response_model=ConfirmResponse)
def confirm_ride(request: ConfirmRequest, token: str = Header(...)):
    if token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token provided.")

    global latest_rides, confirmed_ride

    if not latest_rides:
        raise HTTPException(status_code=400, detail="No rides have been requested yet.")

    if request.option_index < 0 or request.option_index >= len(latest_rides):
        raise HTTPException(status_code=400, detail="Invalid ride option index.")

    chosen_ride = latest_rides[request.option_index]
    confirmed_ride = chosen_ride

    return ConfirmResponse(
        message="Ride confirmed",
        chosen_ride=chosen_ride
    )

@app.post("/cancel", response_model=CancelResponse)
def cancel_ride(token: str = Header(...)):
    if token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token provided.")

    global confirmed_ride
    if confirmed_ride is None:
        raise HTTPException(status_code=400, detail="No ride has been confirmed yet.")

    ride_to_cancel = confirmed_ride
    confirmed_ride = None

    return CancelResponse(
        message=f"Your ride '{ride_to_cancel.name}' was canceled successfully."
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )
