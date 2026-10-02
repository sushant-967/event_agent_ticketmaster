import httpx

from langchain.tools import tool
from typing import Any


from backend.config import (
    TICKETMASTER_API_KEY,
    TICKETMASTER_BASE_URL
)



@tool 
def search_events_by_location(location: str,country_code: str | None = None)->list[dict[str,Any]]:
    """
    Search Ticketmaster events based on a location.
    """
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": location,
        "countryCode":country_code,
        "size": 5
    }
    url = f"{TICKETMASTER_BASE_URL}/events.json"
    response = httpx.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    events = data.get("_embedded", {}).get("events", [])
    result = []
    if not events:
        return [{"message": f"No events found for {location}."}]

    for event in events:
        dates = event.get("dates", {}).get("start", {})

        venues = event.get("_embedded", {}).get("venues", [])
        venue = venues[0] if venues else {}

        images = event.get("images", [])

        result.append({
            "id": event.get("id"),
            "name": event.get("name"),
            "date": dates.get("localDate"),
            "time": dates.get("localTime"),
            "venue": venue.get("name"),
            "city": venue.get("city", {}).get("name"),
            "image": images[0].get("url") if images else None,
            "url": event.get("url"),
        })
    
    
    return result


@tool 
def get_event_details(event_id:str):
    """
    Get detailed information about a specific Ticketmaster event.
    """
    params = {
            "apikey": TICKETMASTER_API_KEY
        }
    url = f"{TICKETMASTER_BASE_URL}/events/{event_id}.json"
    response = httpx.get(url, params=params)
    response.raise_for_status()
    event = response.json()
    venue = (
        event.get("_embedded", {})
        .get("venues", [{}])[0]
    )

    return {
        "id": event.get("id"),
        "name": event.get("name"),
        "description": event.get("description"),
        "date": event.get("dates", {})
                     .get("start", {})
                     .get("localDate"),
        "time": event.get("dates", {})
                     .get("start", {})
                     .get("localTime"),
        "venue": venue.get("name"),
        "address": venue.get("address", {}).get("line1"),
        "city": venue.get("city", {}).get("name"),
        "country": venue.get("country", {}).get("name"),
        "url": event.get("url"),
        "images": event.get("images", [])
    }
    

@tool
def get_event_price(event_id: str) -> dict:
    """
    Retrieve ticket pricing information for an event if available.
    """

    response = httpx.get(
        f"{TICKETMASTER_BASE_URL}/events/{event_id}.json",
        params={
            "apikey": TICKETMASTER_API_KEY
        },
        timeout=15
    )

    response.raise_for_status()

    event = response.json()

    price_ranges = event.get("priceRanges", [])

    if not price_ranges:
        return {
            "event_id": event_id,
            "pricing_available": False,
            "message": "No ticket pricing information available."
        }

    prices = []

    for price in price_ranges:
        prices.append({
            "min": price.get("min"),
            "max": price.get("max"),
            "currency": price.get("currency")
        })

    return {
        "event_id": event_id,
        "pricing_available": True,
        "prices": prices
    }
