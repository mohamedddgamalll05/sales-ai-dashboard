"""
Quick script to view all your data in MongoDB
Run this to see what's actually stored in the database.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from database import db, users_col, predictions_col, dataset_col, models_col
    
    print("=" * 70)
    print("VIEWING YOUR MONGODB DATA")
    print("=" * 70)
    print()
    
    # Database info
    print(f"📊 Database: {db.name}")
    print()
    
    # List all collections
    collections = db.list_collection_names()
    print(f"📁 Collections: {collections}")
    print()
    
    # Users
    print("-" * 70)
    print("👤 USERS COLLECTION")
    print("-" * 70)
    user_count = users_col.count_documents({})
    print(f"Total users: {user_count}")
    print()
    
    if user_count > 0:
        users = list(users_col.find({}, {"password": 0}))  # Don't show password
        for i, user in enumerate(users, 1):
            print(f"User {i}:")
            print(f"  ID: {user.get('_id')}")
            print(f"  Name: {user.get('name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Created: {user.get('created_at')}")
            print()
    else:
        print("⚠️  No users found")
    print()
    
    # Predictions
    print("-" * 70)
    print("🤖 PREDICTIONS COLLECTION")
    print("-" * 70)
    prediction_count = predictions_col.count_documents({})
    print(f"Total predictions: {prediction_count}")
    print()
    
    if prediction_count > 0:
        predictions = list(predictions_col.find({}).sort("created_at", -1).limit(10))
        for i, pred in enumerate(predictions, 1):
            print(f"Prediction {i}:")
            print(f"  User ID: {pred.get('user_id')}")
            print(f"  Input: Quantity={pred.get('input_data', {}).get('quantity')}, Price={pred.get('input_data', {}).get('sales_price')}")
            print(f"  Prediction: {'Good' if pred.get('prediction') == 1 else 'Bad'}")
            print(f"  Model Version: {pred.get('model_version')}")
            print(f"  Created: {pred.get('created_at')}")
            print()
    else:
        print("⚠️  No predictions found")
    print()
    
    # Dataset
    print("-" * 70)
    print("📊 DATASET COLLECTION")
    print("-" * 70)
    dataset_count = dataset_col.count_documents({})
    print(f"Total records: {dataset_count}")
    print()
    
    # Models
    print("-" * 70)
    print("🧠 MODELS COLLECTION")
    print("-" * 70)
    model_count = models_col.count_documents({})
    print(f"Total models: {model_count}")
    print()
    
    if model_count > 0:
        models = list(models_col.find({}, {"model_binary": 0}))  # Don't show binary data
        for i, model in enumerate(models, 1):
            print(f"Model {i}:")
            print(f"  Name: {model.get('model_name')}")
            print(f"  Version: {model.get('version')}")
            print(f"  Trained: {model.get('trained_at')}")
            print()
    else:
        print("⚠️  No models found")
    print()
    
    print("=" * 70)
    print("✅ Data viewing complete!")
    print("=" * 70)
    print()
    print("💡 To view in MongoDB Compass:")
    print("   Connection String:")
    print("   mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db")
    print()
    
except Exception as e:
    import traceback
    print()
    print("=" * 70)
    print("❌ ERROR!")
    print("=" * 70)
    print(f"Error: {e}")
    print()
    print("Full traceback:")
    print(traceback.format_exc())
    print()
    print("Troubleshooting:")
    print("1. Make sure backend is in the correct location")
    print("2. Check MongoDB connection")
    print("3. Run: python backend/test_db_connection.py")
    sys.exit(1)


