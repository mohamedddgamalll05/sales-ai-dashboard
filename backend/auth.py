import hashlib
from datetime import datetime

from bson import ObjectId

from database import users_col


def hash_password(password: str) -> str:
    """
    Hash a password using SHA256.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def signup_user(name: str, email: str, password: str) -> bool:
    """
    Create a new user document if the email is not already taken.
    """
    try:
        # Check if user already exists
        existing_user = users_col.find_one({"email": email})
        if existing_user:
            print(f"⚠️ User with email {email} already exists")
            return False

        # Create new user document
        user_doc = {
            "name": name,
            "email": email,
            "password": hash_password(password),
            "created_at": datetime.utcnow(),
        }
        
        print(f"📝 Inserting user document: {email}")
        result = users_col.insert_one(user_doc)
        
        if result.inserted_id:
            print(f"✅ User inserted successfully with _id: {result.inserted_id}")
            return True
        else:
            print(f"❌ Failed to insert user: No inserted_id returned")
            return False
            
    except Exception as e:
        import traceback
        print(f"❌ Error in signup_user: {e}")
        print(traceback.format_exc())
        raise


def login_user(email: str, password: str):
    """
    Authenticate a user by email/password.
    Returns a safe user payload (no password hash) on success, otherwise None.
    """
    user = users_col.find_one({"email": email})
    if not user:
        return None

    if user["password"] != hash_password(password):
        return None

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at"),
    }


def get_user_by_id(user_id: str):
    """
    Fetch a user document by its stringified ObjectId and return a safe payload.
    """
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        return None

    user = users_col.find_one({"_id": obj_id})
    if not user:
        return None

    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at"),
    }