# Where Your Data is Stored

## 📍 Database: `sales_db` (MongoDB Atlas)

All data is stored in MongoDB Atlas cloud database. Here's exactly where everything goes:

---

## 1. 👤 SIGN UP / USER CREATION DATA

### Collection: `users`

**Location:** `sales_db.users` collection

**What gets stored when you sign up:**
```javascript
{
  "_id": ObjectId("..."),           // Auto-generated unique ID
  "name": "John Doe",                // Your name from signup form
  "email": "john@example.com",       // Your email from signup form
  "password": "hashed_password",     // Your password (SHA256 hashed)
  "created_at": ISODate("2025-12-26T...")  // Timestamp when account created
}
```

**Code Location:**
- File: `backend/auth.py`
- Function: `signup_user()` (line 16-31)
- Endpoint: `POST /signup` in `backend/main.py` (line 106-111)

**How to View in MongoDB:**
```javascript
// In MongoDB Compass or mongosh
use sales_db
db.users.find().pretty()

// Find specific user
db.users.find({ email: "your@email.com" })
```

---

## 2. 🤖 AI INSIGHTS / PREDICTIONS DATA

### Collection: `predictions`

**Location:** `sales_db.predictions` collection

**What gets stored when you make a prediction:**
```javascript
{
  "_id": ObjectId("..."),                    // Auto-generated unique ID
  "user_id": "67890abcdef1234567890123",     // Your user ID (from login)
  "input_data": {
    "quantity": 100,                         // Quantity you entered
    "sales_price": 50.0                      // Sales price you entered
  },
  "prediction": 1,                           // ML prediction (1 = good, 0 = bad)
  "model_version": "1.0",                    // Version of ML model used
  "created_at": ISODate("2025-12-26T...")    // Timestamp when prediction made
}
```

**Code Location:**
- File: `backend/ml.py`
- Function: `log_prediction()` (line 37-51)
- Endpoint: `POST /predict` in `backend/main.py` (line 177-224)

**How to View in MongoDB:**
```javascript
// In MongoDB Compass or mongosh
use sales_db
db.predictions.find().pretty()

// Find your predictions (replace with your user_id)
db.predictions.find({ user_id: "YOUR_USER_ID" })

// Find all "good" predictions
db.predictions.find({ prediction: 1 })

// Find all "bad" predictions
db.predictions.find({ prediction: 0 })
```

---

## 3. 📊 DATASET DATA

### Collection: `dataset`

**Location:** `sales_db.dataset` collection

**What's stored:**
- Sales data loaded from `data/Book4.xlsx`
- Used for analytics dashboard and ML training

**Schema:**
```javascript
{
  "_id": ObjectId("..."),
  "invoice_type": "Sales",
  "date": ISODate("..."),
  "item": "Product A",
  "quantity": 10,
  "sales_price": 25.0,
  "amount": 250.0,
  "balance": 0
}
```

---

## 4. 🧠 ML MODELS DATA

### Collection: `models`

**Location:** `sales_db.models` collection

**What's stored:**
- Trained ML models (serialized binary data)
- Used for making predictions

**Schema:**
```javascript
{
  "_id": ObjectId("..."),
  "model_name": "sales_classifier",
  "version": "1.0",
  "model_binary": BinData(...),  // Binary model data
  "trained_at": ISODate("...")
}
```

---

## 📋 Complete Data Flow

### Sign Up Flow:
```
User fills signup form
    ↓
POST /signup
    ↓
backend/auth.py → signup_user()
    ↓
MongoDB: sales_db.users.insert_one()
    ↓
Data stored in users collection
```

### AI Insights / Prediction Flow:
```
User enters quantity & sales_price
    ↓
POST /predict
    ↓
backend/ml.py → make_prediction() (loads model)
    ↓
ML model makes prediction
    ↓
backend/ml.py → log_prediction()
    ↓
MongoDB: sales_db.predictions.insert_one()
    ↓
Data stored in predictions collection
```

---

## 🔍 How to View Your Data

### Option 1: MongoDB Compass (GUI - Recommended)

1. **Connect to MongoDB Atlas:**
   - Connection String: `mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority`

2. **Navigate to Collections:**
   - Database: `sales_db`
   - Collections:
     - `users` - Your signup data
     - `predictions` - Your AI insights/predictions
     - `dataset` - Sales dataset
     - `models` - ML models

3. **View Documents:**
   - Click on collection name
   - See all documents in table view
   - Click on document to see details

### Option 2: MongoDB Shell (mongosh)

```bash
# Connect to MongoDB
mongosh "mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db"

# Switch to database
use sales_db

# View all users
db.users.find().pretty()

# View all predictions
db.predictions.find().pretty()

# Count documents
db.users.countDocuments()
db.predictions.countDocuments()

# Find your specific data
db.users.find({ email: "your@email.com" })
db.predictions.find({ user_id: "YOUR_USER_ID" })
```

### Option 3: API Endpoints

**View Users:**
```bash
# Get user profile (replace with your user_id)
GET http://127.0.0.1:8000/profile/{user_id}
```

**View Predictions:**
```bash
# Get predictions by model version
GET http://127.0.0.1:8000/aggregations/predictions-by-model

# Get top users by predictions
GET http://127.0.0.1:8000/aggregations/top-users-predictions
```

---

## 📊 Data Relationships

```
users collection
    ↓ (user_id)
predictions collection
    ↓ (uses)
models collection
    ↓ (trained on)
dataset collection
```

**Example:**
- User signs up → Document created in `users` collection
- User makes prediction → Document created in `predictions` collection with `user_id` linking to user
- Prediction uses model from `models` collection
- Model was trained on data from `dataset` collection

---

## 🔐 Security Notes

1. **Passwords are hashed:**
   - Passwords are NOT stored in plain text
   - They are hashed using SHA256
   - Location: `backend/auth.py` line 9-13

2. **User ID is used for linking:**
   - When you login, you get a `user_id`
   - This `user_id` is used to link your predictions to your account
   - Location: `backend/auth.py` line 46-51

3. **Data Privacy:**
   - Each user can only see their own predictions
   - User data is linked via `user_id` in predictions collection

---

## 📝 Quick Reference

| Data Type | Collection | Key Fields | When Created |
|-----------|-----------|------------|--------------|
| User Account | `users` | name, email, password (hashed) | On signup |
| AI Prediction | `predictions` | user_id, input_data, prediction | On prediction |
| Sales Data | `dataset` | item, quantity, sales_price, amount | On init_project.py |
| ML Model | `models` | model_binary, version | On training |

---

## 🛠️ Useful Queries

### Find all your predictions:
```javascript
// Replace "YOUR_USER_ID" with your actual user_id from login response
db.predictions.find({ user_id: "YOUR_USER_ID" }).sort({ created_at: -1 })
```

### Count your predictions:
```javascript
db.predictions.countDocuments({ user_id: "YOUR_USER_ID" })
```

### Find your account:
```javascript
db.users.find({ email: "your@email.com" })
```

### See all good predictions:
```javascript
db.predictions.find({ prediction: 1 })
```

### See all bad predictions:
```javascript
db.predictions.find({ prediction: 0 })
```

---

**💡 Tip:** Your `user_id` is returned when you login. Save it to query your predictions later!

