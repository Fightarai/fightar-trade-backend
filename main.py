from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

from auth_router import router as auth_router
from api_keys_router import router as api_keys_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(api_keys_router)

@app.get("/")
def root():
    return {"message": "✅ Fightar Trade Backend is LIVE"}
