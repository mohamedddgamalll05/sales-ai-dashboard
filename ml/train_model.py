import io
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from joblib import dump

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from database import db, dataset_col, models_col

# Delay sklearn import to avoid numpy compatibility issues
try:
    from sklearn.linear_model import LogisticRegression
except ImportError as e:
    raise ImportError(
        f"Failed to import sklearn. This is usually a numpy/scikit-learn version mismatch.\n"
        f"Run: python fix_dependencies.py\n"
        f"Original error: {e}"
    )


"""
Train a simple binary classifier on the sales dataset and store
the serialized model inside the MongoDB `models` collection.

This script is idempotent:
- If the `dataset` collection is empty, it will bootstrap it from `../data/Book4.xlsx`
- It always reads from the same database as the FastAPI app (sales_db)
"""

EXCEL_PATH = Path(__file__).parent.parent / "data" / "Book4.xlsx"


def ensure_dataset_loaded():
    """
    Ensure that the dataset collection in MongoDB is populated.
    If it's empty, load from the Excel file in ../data/Book4.xlsx.
    """
    if dataset_col.count_documents({}) > 0:
        return

    # Load from Excel and normalize column names
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(f"Excel file not found at {EXCEL_PATH}")
    
    df = pd.read_excel(EXCEL_PATH)

    # Try to normalize possible raw column names to logical names
    rename_map = {}
    if "Qty" in df.columns:
        rename_map["Qty"] = "quantity"
    if "Sales Price" in df.columns:
        rename_map["Sales Price"] = "sales_price"
    if "Amount" in df.columns:
        rename_map["Amount"] = "amount"

    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # Basic fallback column names if the Excel already has clean names
    if "quantity" not in df.columns and "Qty" in df.columns:
        df["quantity"] = df["Qty"]
    if "sales_price" not in df.columns and "Sales Price" in df.columns:
        df["sales_price"] = df["Sales Price"]

    # Compute amount if missing
    if "amount" not in df.columns and {"quantity", "sales_price"}.issubset(df.columns):
        df["amount"] = df["quantity"] * df["sales_price"]

    # Drop rows without essential fields
    df.dropna(subset=["quantity", "sales_price"], inplace=True)

    # Insert into MongoDB
    records = df.to_dict(orient="records")
    if records:
        try:
            dataset_col.insert_many(records)
            print(f"✅ Loaded {len(records)} records into dataset collection")
        except Exception as e:
            print(f"⚠️ Warning: Some records may already exist. Error: {e}")
            # Try inserting one by one to handle duplicates
            inserted = 0
            for record in records:
                try:
                    dataset_col.insert_one(record)
                    inserted += 1
                except Exception:
                    pass  # Skip duplicates
            if inserted > 0:
                print(f"✅ Inserted {inserted} new records")


def train_and_save_model():
    # Ensure dataset is present
    ensure_dataset_loaded()

    # Reload from MongoDB (guaranteed to exist after ensure_dataset_loaded)
    df = pd.DataFrame(list(dataset_col.find()))
    if df.empty:
        raise RuntimeError("Dataset collection is empty; cannot train model.")

    # Remove MongoDB technical field
    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)

    # Ensure expected numeric columns exist
    required_cols = {"quantity", "sales_price"}
    if not required_cols.issubset(df.columns):
        raise RuntimeError(f"Dataset missing required columns: {required_cols - set(df.columns)}")

    if "amount" not in df.columns:
        df["amount"] = df["quantity"] * df["sales_price"]

    # Binary classification label: HIGH vs LOW value invoices
    df["label"] = (df["amount"] > df["amount"].median()).astype(int)

    X = df[["quantity", "sales_price"]]
    y = df["label"]

    model = LogisticRegression()
    model.fit(X, y)

    # Serialize model in-memory and store in MongoDB
    buffer = io.BytesIO()
    dump(model, buffer)

    try:
        models_col.insert_one(
            {
                "model_name": "sales_classifier",
                "version": "1.0",
                "model_binary": buffer.getvalue(),
                "trained_at": datetime.utcnow(),
            }
        )
        print("✅ Model trained and saved to MongoDB successfully")
    except Exception as e:
        print(f"❌ Error saving model to MongoDB: {e}")
        raise


if __name__ == "__main__":
    train_and_save_model()
