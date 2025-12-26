"""
MongoDB Index Management
Creates indexes for optimal query performance
"""
from database import users_col, predictions_col, dataset_col

def create_indexes():
    """
    Create all necessary indexes for optimal query performance.
    This should be called on application startup.
    """
    try:
        # Index 1: Email index on users collection (for fast login lookups)
        users_col.create_index([("email", 1)], name="email_index", unique=False)
        print("✅ Created index on users.email")
        
        # Index 2: User ID index on predictions collection (for fast user prediction queries)
        predictions_col.create_index([("user_id", 1)], name="user_id_index")
        print("✅ Created index on predictions.user_id")
        
        # Index 3: Created_at index on predictions (for time-based queries)
        predictions_col.create_index([("created_at", -1)], name="created_at_index")
        print("✅ Created index on predictions.created_at")
        
        # Index 4: Amount index on dataset (for analytics queries)
        dataset_col.create_index([("amount", -1)], name="amount_index")
        print("✅ Created index on dataset.amount")
        
        # Index 5: Item index on dataset (for grouping queries)
        dataset_col.create_index([("item", 1)], name="item_index")
        print("✅ Created index on dataset.item")
        
        # Index 6: Invoice type index on dataset (for category queries)
        dataset_col.create_index([("invoice_type", 1)], name="invoice_type_index")
        print("✅ Created index on dataset.invoice_type")
        
        return True
    except Exception as e:
        print(f"⚠️ Warning: Error creating indexes: {e}")
        return False

def get_index_info():
    """
    Get information about all indexes in the database.
    """
    indexes = {
        "users": list(users_col.list_indexes()),
        "predictions": list(predictions_col.list_indexes()),
        "dataset": list(dataset_col.list_indexes())
    }
    return indexes

