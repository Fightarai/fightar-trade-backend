from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGO_URL")
client = MongoClient(uri)

try:
    db = client["fightar"]
    users = db["users"]
    users.insert_one({"email": "test@example.com", "password": "testing123"})
    print("✅ Insert successful!")
except Exception as e:
    print("❌ Insert failed:", e)
