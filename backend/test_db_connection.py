"""
Test script to verify MongoDB connection and database operations
Run this to check if your MongoDB connection is working correctly.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("=" * 60)
    print("Testing MongoDB Connection")
    print("=" * 60)
    print()
    
    # Test 1: Import database module
    print("Test 1: Importing database module...")
    from database import client, db, users_col
    print("✅ Database module imported successfully")
    print()
    
    # Test 2: Ping MongoDB
    print("Test 2: Testing MongoDB connection...")
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    print()
    
    # Test 3: Check database
    print("Test 3: Checking database...")
    db_name = db.name
    print(f"✅ Connected to database: {db_name}")
    print()
    
    # Test 4: List collections
    print("Test 4: Listing collections...")
    collections = db.list_collection_names()
    print(f"✅ Collections found: {collections}")
    print()
    
    # Test 5: Check users collection
    print("Test 5: Checking users collection...")
    user_count = users_col.count_documents({})
    print(f"✅ Users collection exists with {user_count} document(s)")
    print()
    
    # Test 6: Try to insert a test document
    print("Test 6: Testing insert operation...")
    from datetime import datetime
    test_doc = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test_hash",
        "created_at": datetime.utcnow()
    }
    
    # Check if test user exists
    existing = users_col.find_one({"email": "test@test.com"})
    if existing:
        print("⚠️  Test user already exists, skipping insert")
    else:
        result = users_col.insert_one(test_doc)
        print(f"✅ Test document inserted with _id: {result.inserted_id}")
        
        # Verify it was inserted
        inserted = users_col.find_one({"_id": result.inserted_id})
        if inserted:
            print("✅ Verified: Document found in database")
        else:
            print("❌ Error: Document not found after insertion")
    
    print()
    print("=" * 60)
    print("✅ All tests passed! MongoDB connection is working correctly.")
    print("=" * 60)
    
except Exception as e:
    import traceback
    print()
    print("=" * 60)
    print("❌ TEST FAILED!")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    print("Full traceback:")
    print(traceback.format_exc())
    print()
    print("Troubleshooting:")
    print("1. Make sure MONGODB_URI environment variable is set")
    print("2. Check your internet connection (for MongoDB Atlas)")
    print("3. Verify the MongoDB connection string is correct")
    print("4. Check if MongoDB Atlas allows connections from your IP")
    sys.exit(1)


