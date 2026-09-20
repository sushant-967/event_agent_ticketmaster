import os
from dotenv import load_dotenv


load_dotenv()

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TICKETMASTER_BASE_URL = (
    "https://app.ticketmaster.com/discovery/v2"
)

