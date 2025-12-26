import os
from pymongo import MongoClient

# Read MongoDB URI (env variable takes priority)
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority"
)

# Create MongoDB client
client = MongoClient(MONGODB_URI)

# Use database
db = client["sales_db"]

# Collections (IMPORTANT: names must match imports)
users_col = db["users"]
dataset_col = db["dataset"]
transactions_col = db["transactions"]
predictions_col = db["predictions"]
models_col = db["models"]