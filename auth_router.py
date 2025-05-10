from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import pymongo
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGO_URL"))
db = client["fightar"]
users_collection = db["users"]

# JWT Config
SECRET_KEY = "supersecretjwtkey"  # replace with stronger value in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Models
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: str

# Register Endpoint
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

# Login Endpoint with JWT
@router.post("/login")
def login_user(request: LoginRequest):
    user = users_collection.find_one({"username": request.username})
    if not user or not pwd_context.verify(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT token
    to_encode = {
        "sub": user["username"],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# Dependency to verify token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")

# Protected Route
from fastapi import Header

@router.get("/protected")
def protected_route(token: str = Header(...)):
    username = verify_token(token)
    return {"msg": f"Access granted for {username}"}

# Check DB Health
@router.get("/check-db", tags=["auth"])
def check_db():
    try:
        count = users_collection.count_documents({})
        return {"status": "success", "user_count": count}
    except Exception as e:
        return {"status": "error", "details": str(e)}