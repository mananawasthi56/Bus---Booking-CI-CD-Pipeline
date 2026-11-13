import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Bus Booking Platform")

DATABASE_URL = os.getenv("DATABASE_URL")