import httpx

API_KEY = "14AfoYSgtZ8rLogIirc7q2KgSxZ1x8Fx"

url = "https://app.ticketmaster.com/discovery/v2/events.json"

params = {
    "apikey": API_KEY,
    "city": "London",
    "size": 5
}

response = httpx.get(url, params=params)

print(response.status_code)
print(response.json())