from pymongo import MongoClient

# Replace with your actual connection string (this one is safe, no special characters)
uri = "mongodb+srv://fightarofficial2:N7S8dieKY3uUW8h@cluster0.y20poaj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri)

# Print available database names
try:
    print("✅ Connected successfully. Databases available:")
    print(client.list_database_names())
except Exception as e:
    print("❌ Connection failed:", e)
