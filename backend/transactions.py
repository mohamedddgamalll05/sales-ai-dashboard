from bson import ObjectId

from database import client, db


def delete_user_and_predictions(user_id: str):
    """
    Use a MongoDB multi-document transaction to delete a user and all of
    their predictions atomically.
    """
    try:
        obj_id = ObjectId(user_id)
    except Exception as e:
        raise ValueError(f"Invalid user_id format: {user_id}") from e
    
    with client.start_session() as session:
        try:
            with session.start_transaction():
                # Delete user by ObjectId
                user_result = db.users.delete_one({"_id": obj_id}, session=session)
                # Delete predictions by string user_id (as stored in predictions collection)
                predictions_result = db.predictions.delete_many({"user_id": user_id}, session=session)
                
                # Commit transaction
                session.commit_transaction()
                
                return {
                    "users_deleted": user_result.deleted_count,
                    "predictions_deleted": predictions_result.deleted_count
                }
        except Exception as e:
            # Rollback transaction on error
            session.abort_transaction()
            raise Exception(f"Transaction failed: {e}") from e
