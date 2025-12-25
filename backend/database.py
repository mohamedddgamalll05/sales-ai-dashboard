from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")
db = client["final_project"]

users_col = db["users"]
dataset_col = db["dataset"]
predictions_col = db["predictions"]
models_col = db["models"]
