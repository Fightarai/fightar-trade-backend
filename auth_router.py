from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
import pymongo
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGO_URL"))
db = client["fightar"]
users_collection = db["users"]

# JWT Config (move secret to environment for production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretjwtkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Models
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str  # "admin", "client", or "bot"

class LoginRequest(BaseModel):
    username: str
    password: str

# REGISTER
@router.post("/register", tags=["auth"])
def register_user(request: RegisterRequest):
    if request.role not in ["admin", "client", "bot"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_user = users_collection.find_one({"username": request.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(request.password)
    user_data = {
        "username": request.username,
        "email": request.email,
        "password": hashed_password,
        "role": request.role
    }

    users_collection.insert_one(user_data)
    return {"message": "User registered successfully"}

# LOGIN
@router.post("/login", tags=["auth"])
def login_user(request: LoginRequest):
    user = users_collection.find_one({"username": request.username})
    if not user or not pwd_context.verify(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    payload = {
        "sub": user["username"],
        "role": user.get("role", "client"),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# VERIFY TOKEN
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or malformed token")

# PROTECTED ROUTE
@router.get("/protected", tags=["auth"])
def protected_route(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    return {
        "msg": f"Access granted for {payload['sub']}",
        "role": payload['role']
    }

# PROFILE
@router.get("/profile", tags=["auth"])
def get_profile(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header.split(" ")[1]
    payload = verify_token(token)

    return {
        "username": payload["sub"],
        "role": payload.get("role", "unknown")
        "token_expires": payload["exp"]
    }

# ADMIN-ONLY
@router.get("/admin-only", tags=["auth"])
def admin_only(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header.split(" ")[1]
    payload = verify_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")

    return {"msg": f"Welcome Admin {payload['sub']}"}

# DB HEALTH CHECK
@router.get("/check-db", tags=["auth"])
def check_db():
    try:
        count = users_collection.count_documents({})
        return {"status": "success", "user_count": count}
    except Exception as e:
        return {"status": "error", "details": str(e)}