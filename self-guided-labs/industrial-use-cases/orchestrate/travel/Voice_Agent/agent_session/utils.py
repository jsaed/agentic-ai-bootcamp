import requests
from datetime import datetime, timedelta
import dateparser
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def search_places(text_query, field_mask="places.displayName,places.formattedAddress,places.priceLevel"):
    """
    Search for places using Google's Places API via text query.

    Args:
        api_key (str): Your Google Maps API key.
        text_query (str): The text query to search for places.
        field_mask (str): Optional. A comma-separated list of fields to include in the response.

    Returns:
        dict: The response from the Places API.
    """
    api_key = os.getenv("google_maps_api_key")
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
    }
    if field_mask:
        headers["X-Goog-FieldMask"] = field_mask

    data = {
        "textQuery": text_query
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Request failed with status {response.status_code}",
            "details": response.json()
        }


def get_booking_date(user_input):
    """
    Converts natural language time expressions into a specific date.
    
    Args:
        user_input (str): The natural language description of time (e.g., 'tomorrow', 'next Sunday').
    
    Returns:
        str: The parsed date in 'YYYY-MM-DD HH:MM:SS' format, or an error message if parsing fails.
    """
    # Handle "next [day of the week]" explicitly
    days_of_week = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    user_input_lower = user_input.lower()

    # Check for "now" in the input and return current date and time
    if "now" in user_input_lower:
        current_time = datetime.now()
        return current_time.strftime('%Y-%m-%d %H:%M:%S')

    if user_input_lower.startswith("next ") and any(day in user_input_lower for day in days_of_week):
        # Extract the day of the week
        for day, day_index in days_of_week.items():
            if day in user_input_lower:
                today = datetime.now()
                current_weekday = today.weekday()
                days_ahead = (day_index - current_weekday + 7) % 7 + 7  # Skip to the next week
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime('%Y-%m-%d')

    # Fallback to dateparser for other cases
    parsed_date = dateparser.parse(user_input, settings={'PREFER_DATES_FROM': 'future'})

    if parsed_date:
        return parsed_date.strftime('%Y-%m-%d')
    else:
        return "Could not parse the date from the input."

    
    #create a tool to access user infomrations

user_data = {
    "users": [
        {
            "user_id": "12345",
            "name": "John Doe",
            "phone_number": "+91-9876543210",
            "email_address": "johndoe@example.com",
            "home_address": {
                "street": "123 Elm Street",
                "city": "Bengaluru",
                "state": "Karnatka",
                "postal_code": "560002",
                "country": "India"
            },
            "office_address": {
                "company_name": "IBM",
                "street": "EGL D Block",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560001",
                "country": "India"
            }
        },
        {
            "user_id": "67890",
            "name": "Jane Smith",
            "phone_number": "+91-9876543211",
            "email_address": "janesmith@example.com",
            "home_address": {
                "street": "789 Pine Lane",
                "city": "Mumbai",
                "state": "Maharashtra",
                "postal_code": "400001",
                "country": "India"
            },
            "office_address": {
                "company_name": "Innovative Tech Pvt. Ltd.",
                "street": "321 Maple Road",
                "city": "Hyderabad",
                "state": "Telangana",
                "postal_code": "500001",
                "country": "India"
            }
        }
    ]
}

def get_user_address(user_id: str, address_type: str) -> dict:
    """
    Retrieves the home or office address of a user by user ID and address type.
    
    Args:
        user_data (dict): JSON data containing user information.
        user_id (str): Unique ID of the user to fetch.
        address_type (str): The type of address to fetch ('home' or 'office').
        
    Returns:
        dict: The requested address if found, else an error message.
    """
    # Validate address_type input
    if address_type not in ["home", "office"]:
        return {"error": "Invalid address type. Please specify 'home' or 'office'."}
    
    # Search for the user by ID
    for user in user_data["users"]:
        if user["user_id"] == user_id:
            if address_type == "home":
                return user.get("home_address", {"error": "Home address not found."})
            elif address_type == "office":
                return user.get("office_address", {"error": "Office address not found."})
    
    return {"error": "User not found"}