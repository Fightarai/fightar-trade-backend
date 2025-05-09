from fastapi import APIRouter, HTTPException, Depends
from user_model import User, Token
from passlib.context import CryptContext
from jose import jwt
import os
import pymongo
from datetime import datetime, timedelta

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_URL"))
db = client["fightar"]
users = db["users"]

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=24)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(user: User):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pw = pwd_context.hash(user.password)
    users.insert_one({"email": user.email, "password": hashed_pw})
    return {"msg": "✅ Registered successfully"}

@router.post("/login", response_model=Token)
def login(user: User):
    record = users.find_one({"email": user.email})
    if not record or not pwd_context.verify(user.password, record["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
