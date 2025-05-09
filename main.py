from fastapi import FastAPI
from dotenv import load_dotenv
import os
from auth_router import router as auth_router

load_dotenv()

app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "✅ Fightar Trade Backend is LIVE"}
