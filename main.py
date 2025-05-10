from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables (for local dev only)
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Fightar API",
    version="1.0.0",
    description="Backend for Fightar Crypto BOT and User Authentication"
)

# ✅ CORS SETTINGS — ADD THIS
origins = [
    "http://localhost:3000",        # Local dev frontend
    "https://fightar.ai",           # (Optional) Production domain
    "https://www.fightar.ai"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],            # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],            # Allow any headers
)

# Import all route modules
from auth_router import router as auth_router
from api_keys_router import router as api_keys_router

# Register routers with prefixes and tags
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(api_keys_router, prefix="/keys", tags=["api_keys"])

# Basic health check
@app.get("/ping")
def ping():
    return {"msg": "This is the latest deployment ✅"}