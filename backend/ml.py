import io
from datetime import datetime

import joblib

from database import db, predictions_col


def load_latest_model():
    """
    Load the most recently trained model from the `models` collection.
    """
    try:
        model_doc = db.models.find_one(sort=[("trained_at", -1)])
        if not model_doc:
            raise Exception("No model found in database. Please train a model first using /train-model endpoint or run ml/train_model.py")

        if "model_binary" not in model_doc:
            raise Exception("Model document is corrupted - missing model_binary field")

        model = joblib.load(io.BytesIO(model_doc["model_binary"]))
        return model, model_doc.get("version", "1.0")
    except Exception as e:
        raise Exception(f"Failed to load model: {e}") from e


def make_prediction(quantity: float, sales_price: float):
    """
    Run model inference for a single (quantity, sales_price) pair.
    Returns (prediction_int, model_version).
    """
    model, version = load_latest_model()
    prediction = int(model.predict([[quantity, sales_price]])[0])
    return prediction, version


def log_prediction(user_id, quantity: float, sales_price: float, prediction: int, model_version: str):
    """
    Persist the prediction in the `predictions` collection.
    """
    doc = {
        "user_id": user_id,
        "input_data": {
            "quantity": quantity,
            "sales_price": sales_price,
        },
        "prediction": prediction,
        "model_version": model_version,
        "created_at": datetime.utcnow(),
    }
    predictions_col.insert_one(doc)
