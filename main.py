from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load .env before anything else
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Import routers after .env is loaded
from auth_router import router as auth_router
from api_keys_router import router as api_keys_router

# Include all routers
app.include_router(auth_router)
app.include_router(api_keys_router)

@app.get("/")
def root():
    return {"message": "✅ Fightar Trade Backend is LIVE"}
