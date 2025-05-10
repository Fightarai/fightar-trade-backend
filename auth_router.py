from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from passlib.context import CryptContext
import pymongo
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGODB_URL"))
db = client["fightar"]
users_collection = db["users"]

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
def register_user(request: RegisterRequest):
    existing_user = users_collection.find_one({"username": request.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(request.password)
    user_data = {
        "username": request.username,
        "email": request.email,
        "password": hashed_password,
    }

    users_collection.insert_one(user_data)
    return {"message": "User registered successfully"}



@router.get("/check-db", tags=["auth"])
def check_db():
    try:
        count = users_collection.count_documents({})
        return {"status": "success", "user_count": count}
    except Exception as e:
        return {"status": "error", "details": str(e)}

