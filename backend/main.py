from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from auth import get_user_by_id, login_user, signup_user
from analytics import get_dashboard_data
from ml import log_prediction, make_prediction
from transactions import delete_user_and_predictions
from database import dataset_col, models_col, client, users_col, predictions_col
from indexes import create_indexes
from aggregations import (
    get_total_sales, get_average_quantity, get_median_amount,
    get_top_items_by_amount, get_category_frequencies, get_distribution_stats,
    get_predictions_by_model_version, get_users_with_most_predictions
)

# Suppress noisy cancellation errors during shutdown (these are harmless)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        # Test MongoDB connection on startup
        client.admin.command('ping')
        print("✅ MongoDB connection verified on startup")
        
        # Create indexes for optimal performance
        print("📊 Creating MongoDB indexes...")
        create_indexes()
        print("✅ Indexes created successfully")
    except Exception as e:
        print(f"⚠️ Warning: MongoDB connection check failed on startup: {e}")
        print("   The server will still start, but database operations may fail.")
    
    yield
    
    # Shutdown
    executor.shutdown(wait=False)
    print("✅ Server shutdown complete")

app = FastAPI(
    title="Sales AI Dashboard API", 
    version="1.0.0",
    lifespan=lifespan
)

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
@app.get("/")
def root():
    """
    Root endpoint - redirects to API documentation.
    """
    return {
        "message": "Sales AI Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "signup": "POST /signup",
            "login": "POST /login",
            "dashboard": "GET /dashboard",
            "profile": "GET /profile/{user_id}",
            "predict": "POST /predict",
            "delete_account": "DELETE /delete-account",
            "health": "GET /health",
            "load_dataset": "POST /load-dataset",
            "train_model": "POST /train-model"
        }
    }

@app.post("/signup")
def signup(data: Signup):
    """
    Create a new user account.
    """
    try:
        print(f"📝 Signup request received: email={data.email}, name={data.name}")
        
        # Verify database connection
        try:
            client.admin.command('ping')
            print("✅ MongoDB connection verified")
        except Exception as db_error:
            print(f"❌ MongoDB connection error: {db_error}")
            return {
                "success": False,
                "message": "Database connection failed. Please check your MongoDB connection.",
                "error": str(db_error)
            }
        
        # Attempt to create user
        success = signup_user(data.name, data.email, data.password)
        
        if not success:
            print(f"⚠️ Signup failed: User with email {data.email} already exists")
            return {"success": False, "message": "User already exists"}
        
        print(f"✅ User created successfully: {data.email}")
        
        # Verify user was created
        user = users_col.find_one({"email": data.email})
        if user:
            print(f"✅ Verified: User document exists in database with _id: {user.get('_id')}")
        else:
            print(f"⚠️ Warning: User document not found after creation")
        
        return {"success": True, "message": "Account created successfully"}
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error in signup endpoint: {e}")
        print(error_details)
        return {
            "success": False,
            "message": "Failed to create account. Please try again.",
            "error": str(e)
        }

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


# ---------------- AGGREGATION ENDPOINTS (BONUS) ----------------
@app.get("/aggregations/total-sales")
def aggregation_total_sales():
    """
    MongoDB Aggregation: Total sales (equivalent to pandas df['amount'].sum())
    """
    try:
        result = get_total_sales()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/aggregations/average-quantity")
def aggregation_average_quantity():
    """
    MongoDB Aggregation: Average quantity (equivalent to pandas df['quantity'].mean())
    """
    try:
        result = get_average_quantity()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/aggregations/median-amount")
def aggregation_median_amount():
    """
    MongoDB Aggregation: Median amount (equivalent to pandas df['amount'].median())
    """
    try:
        result = get_median_amount()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/aggregations/top-items")
def aggregation_top_items(limit: int = 10):
    """
    MongoDB Aggregation: Top items by total amount
    """
    try:
        result = get_top_items_by_amount(limit)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/aggregations/category-frequencies")
def aggregation_category_frequencies():
    """
    MongoDB Aggregation: Category frequencies (equivalent to pandas value_counts())
    """
    try:
        result = get_category_frequencies()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/aggregations/distribution-stats")
def aggregation_distribution_stats():
    """
    MongoDB Aggregation: Distribution statistics (equivalent to pandas describe())
    """
    try:
        result = get_distribution_stats()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/aggregations/predictions-by-model")
def aggregation_predictions_by_model():
    """
    MongoDB Aggregation: Count predictions by model version
    """
    try:
        result = get_predictions_by_model_version()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/aggregations/top-users-predictions")
def aggregation_top_users_predictions(limit: int = 10):
    """
    MongoDB Aggregation: Users with most predictions
    """
    try:
        result = get_users_with_most_predictions(limit)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------- INDEXING & EXPLAIN ENDPOINTS ----------------
@app.get("/indexes/info")
def indexes_info():
    """
    Get information about all indexes in the database.
    """
    try:
        from indexes import get_index_info
        indexes = get_index_info()
        return {"success": True, "indexes": indexes}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/explain/query")
def explain_query(
    collection: str,
    query_field: str = "email",
    query_value: str = "test@test.com"
):
    """
    Demonstrate explain() for query performance analysis.
    Shows execution stats including index usage.
    
    Parameters:
    - collection: users, predictions, or dataset
    - query_field: Field to query on
    - query_value: Value to search for
    """
    try:
        # Select collection
        if collection == "users":
            col = users_col
        elif collection == "predictions":
            col = predictions_col
        elif collection == "dataset":
            col = dataset_col
        else:
            return {"success": False, "error": "Invalid collection. Use: users, predictions, or dataset"}
        
        # Build query
        query = {query_field: query_value}
        
        # Get explain results
        explain_result = col.find(query).explain("executionStats")
        
        # Extract key metrics
        execution_stats = explain_result.get("executionStats", {})
        execution_stages = execution_stats.get("executionStages", {})
        
        result = {
            "collection": collection,
            "query": query,
            "execution_time_ms": execution_stats.get("executionTimeMillis", 0),
            "total_docs_examined": execution_stats.get("totalDocsExamined", 0),
            "total_docs_returned": execution_stats.get("nReturned", 0),
            "stage": execution_stages.get("stage", "UNKNOWN"),
            "index_used": execution_stages.get("indexName", "COLLSCAN (No index)"),
            "full_explain": explain_result
        }
        
        return {"success": True, "data": result}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
