from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from auth import get_user_by_id, login_user, signup_user
from analytics import get_dashboard_data
from ml import log_prediction, make_prediction
from transactions import delete_user_and_predictions
from database import dataset_col, models_col

# Suppress noisy cancellation errors during shutdown (these are harmless)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

app = FastAPI(title="Sales AI Dashboard API", version="1.0.0")

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=2)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    executor.shutdown(wait=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------
class Signup(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class PredictionInput(BaseModel):
    user_id: str
    quantity: float
    sales_price: float

class DeleteAccountInput(BaseModel):
    user_id: str

# ---------------- ROUTES ----------------
@app.post("/signup")
def signup(data: Signup):
    success = signup_user(data.name, data.email, data.password)
    if not success:
        return {"success": False, "message": "User already exists"}
    return {"success": True}

@app.post("/login")
def login(data: Login):
    user = login_user(data.email, data.password)
    if not user:
        return {"success": False, "message": "Invalid credentials"}
    return {"success": True, "user": user}

@app.get("/dashboard")
async def dashboard():
    try:
        # Run analytics in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, get_dashboard_data)
    except asyncio.CancelledError:
        # Suppress cancellation errors during shutdown
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in dashboard endpoint: {e}")
        print(error_details)
        return {
            "stats": {
                "total_sales": 0,
                "average_quantity": 0,
                "median_quantity": 0,
                "invoice_count": 0,
                "category_frequencies": {},
            },
            "charts": {
                "item_sales": None,
                "amount_distribution": None,
                "pie_chart": None,
            },
            "error": str(e),
        }


@app.get("/profile/{user_id}")
def profile(user_id: str):
    """
    Return the current user's profile information.
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            return {"success": False, "message": "User not found"}
        return {"success": True, "user": user}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in profile endpoint: {e}")
        print(error_details)
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to load profile"
        }


def _make_prediction_sync(quantity: float, sales_price: float):
    """Synchronous prediction function - runs in thread pool"""
    return make_prediction(quantity, sales_price)

@app.post("/predict")
async def predict(data: PredictionInput):
    """
    Run an ML prediction and log the result in the `predictions` collection.
    """
    try:
        # Validate input
        if data.quantity <= 0 or data.sales_price < 0:
            return {
                "success": False,
                "error": "Quantity must be positive and sales price must be non-negative"
            }
        
        # Run prediction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        prediction, version = await loop.run_in_executor(
            executor, 
            _make_prediction_sync, 
            data.quantity, 
            data.sales_price
        )
        
        log_prediction(
            user_id=data.user_id,
            quantity=data.quantity,
            sales_price=data.sales_price,
            prediction=prediction,
            model_version=version,
        )

        label = "good" if prediction == 1 else "bad"
        return {
            "success": True,
            "prediction": int(prediction),
            "label": label,
            "model_version": version,
        }
    except asyncio.CancelledError:
        # Suppress cancellation errors during shutdown
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in predict endpoint: {e}")
        print(error_details)
        return {
            "success": False,
            "error": str(e),
            "message": "Prediction failed. Make sure a model is trained."
        }


@app.delete("/delete-account")
def delete_account(payload: DeleteAccountInput):
    """
    Delete the current user and all their predictions using a transaction.
    """
    try:
        result = delete_user_and_predictions(payload.user_id)
        return {
            "success": True,
            "users_deleted": result.get("users_deleted", 0),
            "predictions_deleted": result.get("predictions_deleted", 0)
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error deleting account: {e}")
        print(error_details)
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to delete account"
        }


@app.get("/health")
def health_check():
    """
    Health check endpoint to verify backend is running.
    """
    try:
        from database import client, dataset_col
        # Test MongoDB connection
        client.admin.command('ping')
        dataset_count = dataset_col.count_documents({})
        model_count = models_col.count_documents({})
        return {
            "status": "healthy",
            "mongodb": "connected",
            "dataset_count": dataset_count,
            "model_count": model_count
        }
    except Exception as e:
        return {"status": "unhealthy", "mongodb": "disconnected", "error": str(e)}


def _load_dataset_sync():
    """Synchronous function to load dataset - runs in thread pool"""
    import sys
    from pathlib import Path
    # Add ml directory to path for import
    ml_path = str(Path(__file__).parent.parent / "ml")
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)
    # Import after adding to path
    import train_model  # type: ignore
    train_model.ensure_dataset_loaded()
    return dataset_col.count_documents({})

@app.post("/load-dataset")
async def load_dataset():
    """
    Load dataset from Excel file into MongoDB.
    Useful for initializing the database.
    """
    try:
        # Run blocking operation in thread pool
        loop = asyncio.get_event_loop()
        dataset_count = await loop.run_in_executor(executor, _load_dataset_sync)
        
        return {
            "success": True,
            "message": f"Dataset loaded successfully. {dataset_count} records found.",
            "count": dataset_count
        }
    except asyncio.CancelledError:
        # Suppress cancellation errors during shutdown
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error loading dataset: {e}")
        print(error_details)
        return {
            "success": False,
            "error": str(e),
            "details": error_details
        }


def _train_model_sync():
    """Synchronous function to train model - runs in thread pool"""
    import sys
    from pathlib import Path
    # Add ml directory to path for import
    ml_path = str(Path(__file__).parent.parent / "ml")
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)
    # Import after adding to path
    import train_model  # type: ignore
    train_model.train_and_save_model()
    return models_col.count_documents({})

@app.post("/train-model")
async def train_model_endpoint():
    """
    Train and save ML model to MongoDB.
    """
    try:
        # Run blocking operation in thread pool
        loop = asyncio.get_event_loop()
        model_count = await loop.run_in_executor(executor, _train_model_sync)
        
        return {
            "success": True,
            "message": f"Model trained and saved successfully. {model_count} model(s) in database.",
            "count": model_count
        }
    except asyncio.CancelledError:
        # Suppress cancellation errors during shutdown
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error training model: {e}")
        print(error_details)
        return {
            "success": False,
            "error": str(e),
            "details": error_details
        }
