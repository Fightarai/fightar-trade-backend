from fastapi import APIRouter, HTTPException, Request, Header
from jose import jwt, JWTError
from cryptography.fernet import Fernet
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ENCRYPTION_KEY = Fernet.generate_key()  # Should be fixed & saved securely later
fernet = Fernet(ENCRYPTION_KEY)

# MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_URL"))
db = client["fightar"]
apikeys = db["api_keys"]

# ✅ Token verifier
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# 🔐 Save Binance API Keys
@router.post("/api-keys")
def save_api_keys(
    request: Request,
    api_key: str,
    api_secret: str,
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    encrypted_key = fernet.encrypt(api_key.encode()).decode()
    encrypted_secret = fernet.encrypt(api_secret.encode()).decode()

    apikeys.update_one(
        {"email": email},
        {"$set": {"api_key": encrypted_key, "api_secret": encrypted_secret}},
        upsert=True
    )

    return {"message": "✅ API keys saved securely"}

# 🔍 Get Keys (for testing — restrict in production)
@router.get("/api-keys")
def get_api_keys(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    record = apikeys.find_one({"email": email})
    if not record:
        raise HTTPException(status_code=404, detail="Keys not found")

    decrypted_key = fernet.decrypt(record["api_key"].encode()).decode()
    decrypted_secret = fernet.decrypt(record["api_secret"].encode()).decode()

    return {
        "api_key": decrypted_key,
        "api_secret": decrypted_secret
    }
