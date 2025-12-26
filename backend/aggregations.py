"""
MongoDB Aggregation Pipelines
Reproducing Pandas Statistics using MongoDB Aggregation
"""
from database import dataset_col, predictions_col, users_col

def get_total_sales():
    """Total sales (sum of all amounts) - Equivalent to pandas: df['amount'].sum()"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_sales": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    result = list(dataset_col.aggregate(pipeline))
    return result[0] if result else {"total_sales": 0, "count": 0}

def get_average_quantity():
    """Average quantity - Equivalent to pandas: df['quantity'].mean()"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "average_quantity": {"$avg": "$quantity"},
                "min_quantity": {"$min": "$quantity"},
                "max_quantity": {"$max": "$quantity"}
            }
        }
    ]
    result = list(dataset_col.aggregate(pipeline))
    return result[0] if result else {"average_quantity": 0, "min_quantity": 0, "max_quantity": 0}

def get_median_amount():
    """Median amount - Equivalent to pandas: df['amount'].median()"""
    pipeline = [
        {"$sort": {"amount": 1}},
        {
            "$group": {
                "_id": None,
                "amounts": {"$push": "$amount"},
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "median_index": {"$floor": {"$divide": ["$count", 2]}},
                "amounts": 1,
                "count": 1
            }
        }
    ]
    result = list(dataset_col.aggregate(pipeline))
    if result and result[0].get("amounts"):
        amounts = result[0]["amounts"]
        median_idx = result[0]["median_index"]
        median = amounts[median_idx] if median_idx < len(amounts) else 0
        return {"median_amount": median, "count": result[0]["count"]}
    return {"median_amount": 0, "count": 0}

def get_top_items_by_amount(limit=10):
    """Top items by total amount - Equivalent to pandas groupby"""
    pipeline = [
        {
            "$group": {
                "_id": "$item",
                "total_amount": {"$sum": "$amount"},
                "total_quantity": {"$sum": "$quantity"},
                "invoice_count": {"$sum": 1}
            }
        },
        {"$sort": {"total_amount": -1}},
        {"$limit": limit}
    ]
    return list(dataset_col.aggregate(pipeline))

def get_category_frequencies():
    """Category frequencies - Equivalent to pandas: df['invoice_type'].value_counts()"""
    pipeline = [
        {
            "$group": {
                "_id": "$invoice_type",
                "count": {"$sum": 1},
                "total_amount": {"$sum": "$amount"}
            }
        },
        {"$sort": {"count": -1}}
    ]
    return list(dataset_col.aggregate(pipeline))

def get_distribution_stats():
    """Distribution statistics - Equivalent to pandas describe()"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "count": {"$sum": 1},
                "avg_amount": {"$avg": "$amount"},
                "min_amount": {"$min": "$amount"},
                "max_amount": {"$max": "$amount"},
                "avg_quantity": {"$avg": "$quantity"},
                "avg_sales_price": {"$avg": "$sales_price"}
            }
        }
    ]
    result = list(dataset_col.aggregate(pipeline))
    return result[0] if result else {}

def get_predictions_by_model_version():
    """Count predictions by model version"""
    pipeline = [
        {
            "$group": {
                "_id": "$model_version",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]
    return list(predictions_col.aggregate(pipeline))

def get_users_with_most_predictions(limit=10):
    """Find users with most predictions"""
    pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "prediction_count": {"$sum": 1}
            }
        },
        {"$sort": {"prediction_count": -1}},
        {"$limit": limit}
    ]
    return list(predictions_col.aggregate(pipeline))

def get_date_based_analysis():
    """Date-based analysis grouped by month"""
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m",
                        "date": "$date"
                    }
                },
                "total_sales": {"$sum": "$amount"},
                "invoice_count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    return list(dataset_col.aggregate(pipeline))

