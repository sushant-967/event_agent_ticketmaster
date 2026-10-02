
from langchain.tools import tool
import httpx


from typing import Any


from backend.config import (
    TICKETMASTER_API_KEY,
    TICKETMASTER_BASE_URL
)

@tool
def prepare_booking(event_id:str):
    """
    Prepare a booking request with human approval
    """
    params = {
            "apikey": TICKETMASTER_API_KEY
        }
    url = f"{TICKETMASTER_BASE_URL}/events/{event_id}.json"
    response = httpx.get(url, params=params)
    response.raise_for_status()
    event = response.json()
    print("prepare booking called")
    venue = (
        event.get("_embedded", {})
        .get("venues", [{}])[0]
    )    
    return {
            "id": event.get("id"),
            "name": event.get("name"),
            "url":event.get("url")
    }

