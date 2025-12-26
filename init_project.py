"""
Complete project initialization script.
This will:
1. Check MongoDB connection
2. Load dataset from Excel
3. Train ML model
4. Verify everything is ready
"""
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("Project Initialization Script")
    print("=" * 60)
    print()
    
    # Step 1: Check MongoDB
    print("Step 1: Checking MongoDB connection...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from database import client
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        
        # Create indexes
        print("   Creating indexes...")
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from indexes import create_indexes
        create_indexes()
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   → Please start MongoDB: mongod")
        print("   → Or check your MONGODB_URI environment variable")
        return False
    print()
    
    # Step 2: Load Dataset
    print("Step 2: Loading dataset from Excel...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "ml"))
        from train_model import ensure_dataset_loaded
        
        ensure_dataset_loaded()
        
        # Verify dataset loaded
        from database import db
        count = db.dataset.count_documents({})
        if count > 0:
            print(f"✅ Dataset loaded successfully: {count} records")
        else:
            print("⚠️  Dataset collection is still empty")
            print("   → Check if Book4.xlsx exists in data/ folder")
            return False
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # Step 3: Train Model
    print("Step 3: Training ML model...")
    try:
        from train_model import train_and_save_model
        train_and_save_model()
        
        # Verify model saved
        from database import models_col
        model_count = models_col.count_documents({})
        if model_count > 0:
            print(f"✅ Model trained and saved: {model_count} model(s)")
        else:
            print("⚠️  No model found in database")
            return False
    except Exception as e:
        print(f"❌ Error training model: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # Step 4: Final verification
    print("Step 4: Final verification...")
    from database import users_col, predictions_col
    user_count = users_col.count_documents({})
    prediction_count = predictions_col.count_documents({})
    
    print(f"✅ Dataset: {count} records")
    print(f"✅ Models: {model_count} model(s)")
    print(f"✅ Users: {user_count} user(s)")
    print(f"✅ Predictions: {prediction_count} prediction(s)")
    print()
    
    print("=" * 60)
    print("✅ Initialization Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start backend: cd backend && uvicorn main:app --reload")
    print("2. Open frontend/dashboard.html in your browser")
    print("3. Create an account and login to see the dashboard")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

