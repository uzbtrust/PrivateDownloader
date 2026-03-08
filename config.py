import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = os.getenv("API_ID", "0")
API_HASH = os.getenv("API_HASH", "")

API_ID = int(API_ID) if API_ID.isdigit() else 0

DB_NAME = "database.db"
SESSION_DIR = "sessions"
DATA_DIR = "data"
