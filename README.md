# Full Stack MongoDB + FastAPI + ML Project

## Quick Start Guide

### 0. Set MongoDB URI (IMPORTANT - Do This First!)

**Windows:**
```bash
setup_mongodb_uri.bat
```
Or manually:
```bash
setx MONGODB_URI "mongodb+srv://sales_user:salesmongo123@cluster0.syv8b7f.mongodb.net/sales_db?retryWrites=true&w=majority"
```

**Linux/Mac:**
```bash
chmod +x setup_mongodb_uri.sh
./setup_mongodb_uri.sh
```

**Note:** After setting the environment variable, restart your terminal/command prompt for it to take effect.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. MongoDB Connection
This project uses MongoDB Atlas (cloud database). The connection string is already configured in `backend/database.py` and can be overridden with the `MONGODB_URI` environment variable.

### 3. Initialize Project (Load Data & Train Model)
**IMPORTANT:** Run this first to populate the dataset and train the model!
```bash
python init_project.py
```
This will:
- Check MongoDB connection
- Load `data/Book4.xlsx` into MongoDB if dataset is empty
- Train the ML model
- Save the model to MongoDB

**Alternative:** If you prefer to do it manually:
```bash
cd ml
python train_model.py
```

### 4. Start FastAPI Backend
```bash
cd backend
uvicorn main:app --reload
```
Backend will run on `http://127.0.0.1:8000`

**Or use the batch file (Windows):**
```bash
start_backend.bat
```

### 5. Open Frontend
Open `frontend/dashboard.html` in your browser (or use Live Server)

**Note:** You must be logged in to view the dashboard. If you don't have an account, create one from the login page.

## Troubleshooting

### Dashboard shows error or all zeros?

1. **"Cannot connect to backend" error**
   - Make sure FastAPI is running: `cd backend && uvicorn main:app --reload`
   - Check it's on port 8000: http://127.0.0.1:8000/health
   - Check browser console (F12) for detailed error messages

2. **Dashboard shows all zeros**
   - Load dataset: Run `python init_project.py` or use the "Load Dataset Now" button on the dashboard
   - Refresh dashboard page (Ctrl+F5)

3. **Charts not showing**
   - Check backend terminal for Python errors
   - Make sure dataset collection has data
   - Check browser console (F12) for JavaScript errors
   - Charts will only appear if there is data in the dataset

4. **MongoDB connection errors**
   - Start MongoDB: `mongod` (or start MongoDB service)
   - Verify connection: `mongosh` should work

5. **Infinite reload loop**
   - Clear browser localStorage: Open browser console (F12) and run `localStorage.clear()`
   - Make sure you're logged in before accessing dashboard

### Quick Test
Visit http://127.0.0.1:8000/health to check if backend is running

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with API information
- `POST /signup` - User registration
- `POST /login` - User authentication
- `GET /dashboard` - Analytics dashboard data
- `GET /profile/{user_id}` - User profile
- `POST /predict` - ML prediction
- `DELETE /delete-account` - Delete user account (with transaction)
- `GET /health` - Health check
- `POST /load-dataset` - Load dataset from Excel
- `POST /train-model` - Train ML model

### Aggregation Endpoints (Bonus)
- `GET /aggregations/total-sales` - Total sales aggregation
- `GET /aggregations/average-quantity` - Average quantity
- `GET /aggregations/median-amount` - Median amount
- `GET /aggregations/top-items?limit=10` - Top items by amount
- `GET /aggregations/category-frequencies` - Category frequencies
- `GET /aggregations/distribution-stats` - Distribution statistics
- `GET /aggregations/predictions-by-model` - Predictions by model version
- `GET /aggregations/top-users-predictions?limit=10` - Top users by predictions

### Indexing & Performance
- `GET /indexes/info` - Get all index information
- `GET /explain/query?collection=users&query_field=email&query_value=test@test.com` - Explain query performance

## Project Features

### ✅ Implemented Requirements

1. **5 Main Pages + Prediction Results**
   - ✅ Sign Up Page (`frontend/signup.html`)
   - ✅ Login Page (`frontend/login.html`)
   - ✅ Analytics Dashboard (`frontend/dashboard.html`)
   - ✅ Profile Page (`frontend/profile.html`)
   - ✅ ML Prediction Page (`frontend/predict.html`)
   - ✅ Good Result Page (`frontend/result_good.html`)
   - ✅ Bad Result Page (`frontend/result_bad.html`)

2. **MongoDB Collections**
   - ✅ Users collection
   - ✅ Dataset collection
   - ✅ Predictions collection
   - ✅ Models collection

3. **CRUD Operations**
   - ✅ **Create**: Signup, Predictions, Dataset loading
   - ✅ **Read**: Login, Dashboard, Profile, Health check
   - ✅ **Update**: (Optional - can be added for password reset)
   - ✅ **Delete**: Delete account with transaction

4. **Indexing**
   - ✅ 6 indexes created automatically on startup
   - ✅ Explain() endpoint for performance analysis
   - ✅ Index information endpoint

5. **Aggregation Pipelines (Bonus)**
   - ✅ 8 aggregation endpoints reproducing Pandas statistics
   - ✅ All aggregations documented in `mongodb/aggregations.js`

6. **Transactions (ACID)**
   - ✅ Delete user and predictions atomically
   - ✅ Transaction rollback demonstration
   - ✅ Implemented in `backend/transactions.py`

7. **ML Integration**
   - ✅ Model training from dataset
   - ✅ Model storage in MongoDB
   - ✅ Model loading and prediction
   - ✅ Prediction logging

8. **Analytics Dashboard**
   - ✅ Pandas statistical measures
   - ✅ Matplotlib/Seaborn visualizations (bar, pie, histogram)
   - ✅ Base64 encoded charts for frontend display

## Project Structure
- `backend/` - FastAPI application
  - `main.py` - Main FastAPI app with all endpoints
  - `database.py` - MongoDB connection and collections
  - `auth.py` - User authentication
  - `analytics.py` - Dashboard analytics and visualizations
  - `ml.py` - ML model loading and prediction
  - `transactions.py` - ACID transactions
  - `indexes.py` - Index management
  - `aggregations.py` - Aggregation pipelines
- `frontend/` - HTML/CSS/JS files
  - All 7 pages (signup, login, dashboard, profile, predict, result_good, result_bad)
- `ml/` - ML training script
  - `train_model.py` - Model training and dataset loading
- `mongodb/` - MongoDB queries, aggregations, indexes, transactions
  - `all_queries_and_transactions.js` - Complete reference file
  - `queries.js` - CRUD operations
  - `aggregations.js` - Aggregation pipelines
  - `indexes.js` - Index creation and explain()
  - `transactions.js` - ACID transactions
- `data/` - Dataset Excel file
- `outputs/` - Generated charts and screenshots
- `Schema.md` - Database schema documentation
- `setup_mongodb_uri.bat` / `.sh` - MongoDB URI setup scripts

## MongoDB Database

**Database Name:** `sales_db`

**Collections:**
- `users` - User accounts
- `dataset` - Sales dataset
- `predictions` - ML predictions
- `models` - Trained ML models

**Indexes (Created Automatically):**
1. `users.email` - For fast login lookups
2. `predictions.user_id` - For user prediction queries
3. `predictions.created_at` - For time-based queries
4. `dataset.amount` - For analytics queries
5. `dataset.item` - For grouping queries
6. `dataset.invoice_type` - For category queries

## Documentation

- **API Documentation:** http://127.0.0.1:8000/docs (Swagger UI)
- **Schema:** See `Schema.md`
- **All Queries:** See `mongodb/all_queries_and_transactions.js`
