from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Import routers
from auth_router import router as auth_router
from api_keys_router import router as api_keys_router

# Initialize app
app = FastAPI()

# Include routers with prefix (fix routing issue)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(api_keys_router, prefix="/keys", tags=["api_keys"])

# Health check
@app.get("/ping")
def ping():
    return {"msg": "This is the latest deployment ✅"}