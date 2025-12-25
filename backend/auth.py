import hashlib
from datetime import datetime

from bson import ObjectId

from database import users_col


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def signup_user(name: str, email: str, password: str) -> bool:
    """
    Create a new user document if the email is not already taken.
    """
    if users_col.find_one({"email": email}):
        return False

    users_col.insert_one(
        {
            "name": name,
            "email": email,
            "password": hash_password(password),
            "created_at": datetime.utcnow(),
        }
    )
    return True


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
